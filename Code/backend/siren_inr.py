"""
SIREN-based implicit neural representation with FiLM conditioning.

Maps continuous coordinates (x, y, t) to RGB using sine activations and
per-layer FiLM modulation derived from text and optional audio embeddings.

Key features:
- SIREN initialization with configurable w0 for first/hidden layers
- Optional separate w0 for time coordinate
- FiLM conditioner that emits per-layer gamma/beta
- Output head with tanh to keep values in [-1, 1] (caller can rescale)
"""

from typing import Optional, Tuple

import torch
import torch.nn as nn


def siren_init_(linear: nn.Linear, w0: float, c: float = 6.0) -> None:
    """Initialize SIREN layer weights per Sitzmann et al. 2020."""
    with torch.no_grad():
        # First layer uses fan_in scaling; hidden layers use uniform with 1/fan_in
        bound = (c / linear.in_features) ** 0.5 if linear.weight is not None else 0.0
        linear.weight.uniform_(-bound / w0, bound / w0)
        if linear.bias is not None:
            linear.bias.zero_()


class FiLMConditioner(nn.Module):
    """Maps conditioning vector to per-layer FiLM parameters."""

    def __init__(
        self,
        cond_dim: int,
        hidden_dim: int,
        num_layers: int,
        film_hidden: int = 64,
        use_bias: bool = True,
    ) -> None:
        super().__init__()
        self.num_layers = num_layers
        self.hidden_dim = hidden_dim

        self.net = nn.Sequential(
            nn.Linear(cond_dim, film_hidden, bias=use_bias),
            nn.ReLU(inplace=True),
            nn.Linear(film_hidden, film_hidden, bias=use_bias),
            nn.ReLU(inplace=True),
            nn.Linear(film_hidden, num_layers * hidden_dim * 2, bias=use_bias),
        )

    def forward(self, cond: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            cond: (batch, cond_dim)
        Returns:
            gammas: (batch, num_layers, hidden_dim)
            betas: (batch, num_layers, hidden_dim)
        """
        params = self.net(cond)
        params = params.view(cond.shape[0], self.num_layers, self.hidden_dim * 2)
        gammas, betas = params.split(self.hidden_dim, dim=-1)
        return gammas, betas


class SirenLayer(nn.Module):
    """Single SIREN layer with optional FiLM modulation."""

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        w0: float,
        use_bias: bool = True,
    ) -> None:
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim, bias=use_bias)
        self.w0 = w0
        siren_init_(self.linear, w0=w0)

    def forward(
        self,
        x: torch.Tensor,
        gamma: Optional[torch.Tensor] = None,
        beta: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        x = self.linear(x)
        if gamma is not None and beta is not None:
            x = x * (1.0 + gamma) + beta
        return torch.sin(self.w0 * x)


class SirenINR(nn.Module):
    """SIREN INR with FiLM modulation from text (+ optional audio) embeddings."""

    def __init__(
        self,
        coord_dim: int = 3,
        hidden_dim: int = 8,
        num_layers: int = 3,
        out_dim: int = 3,
        cond_dim: int = 512,
        w0_first: float = 30.0,
        w0_hidden: float = 1.0,
        w0_time: Optional[float] = None,
        film_hidden: int = 64,
        output_activation: str = "tanh",
        use_bias: bool = True,
    ) -> None:
        """
        Args:
            coord_dim: input coordinate dimension (x, y, t) => 3
            hidden_dim: hidden width for SIREN layers
            num_layers: number of hidden layers (>=1)
            out_dim: output channels (RGB)
            cond_dim: conditioning vector dimension (e.g., CLIP text + audio)
            w0_first: frequency factor for first layer
            w0_hidden: frequency factor for hidden layers
            w0_time: optional separate scaling for time coordinate
            film_hidden: hidden width for FiLM conditioner
            output_activation: "tanh" or "sigmoid"
            use_bias: include biases in linear layers
        """
        super().__init__()
        assert num_layers >= 1, "num_layers must be >= 1"

        self.coord_dim = coord_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.out_dim = out_dim
        self.w0_first = w0_first
        self.w0_hidden = w0_hidden
        self.w0_time = w0_time
        self.output_activation = output_activation

        layers = []
        layers.append(SirenLayer(coord_dim, hidden_dim, w0=w0_first, use_bias=use_bias))
        for _ in range(num_layers - 1):
            layers.append(SirenLayer(hidden_dim, hidden_dim, w0=w0_hidden, use_bias=use_bias))
        self.layers = nn.ModuleList(layers)

        self.final_linear = nn.Linear(hidden_dim, out_dim, bias=use_bias)
        siren_init_(self.final_linear, w0=1.0)

        self.conditioner = FiLMConditioner(
            cond_dim=cond_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            film_hidden=film_hidden,
            use_bias=use_bias,
        )

    def forward(
        self,
        coords: torch.Tensor,
        cond: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            coords: (batch, coord_dim) normalized to [-1, 1]
            cond: (batch, cond_dim) conditioning vector (text [+ audio])
        Returns:
            rgb: (batch, out_dim) in [-1, 1] if tanh, else [0, 1] if sigmoid
        """
        if self.w0_time is not None and coords.shape[1] >= 3:
            coords = coords.clone()
            coords[:, 2] = coords[:, 2] * self.w0_time

        gammas, betas = self.conditioner(cond)

        x = coords
        for idx, layer in enumerate(self.layers):
            gamma_i = gammas[:, idx, :] if gammas is not None else None
            beta_i = betas[:, idx, :] if betas is not None else None
            x = layer(x, gamma=gamma_i, beta=beta_i)

        x = self.final_linear(x)

        if self.output_activation == "tanh":
            x = torch.tanh(x)
        elif self.output_activation == "sigmoid":
            x = torch.sigmoid(x)
        else:
            raise ValueError(f"Unknown output_activation: {self.output_activation}")

        return x

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


