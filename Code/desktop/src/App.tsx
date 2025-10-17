import { useState } from "react";
import "./App.css";

function App() {
  const [greetMsg, setGreetMsg] = useState("");
  const [name, setName] = useState("");

  async function greet() {
    // Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
    // const { invoke } = await import("@tauri-apps/api/core");
    // setGreetMsg(await invoke("greet", { name }));
    setGreetMsg(`Hello, ${name}! Welcome to Audio Feature Explorer`);
  }

  return (
    <div className="container">
      <h1>Audio Feature Explorer</h1>
      <p>Tauri + React + TypeScript Setup Complete!</p>

      <div className="row">
        <input
          id="greet-input"
          onChange={(e) => setName(e.currentTarget.value)}
          placeholder="Enter a name..."
        />
        <button type="button" onClick={() => greet()}>
          Greet
        </button>
      </div>
      <p>{greetMsg}</p>
    </div>
  );
}

export default App;

