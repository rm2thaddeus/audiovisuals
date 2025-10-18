# Week 2: Integration Testing - Quick Checklist

**Goal:** Test the Python integration you built in Week 1  
**Duration:** ~1 hour (mostly waiting for installations)

---

## ☑️ Pre-Testing: Install Toolchain

### Task 1: Install Node.js
```powershell
# Download from: https://nodejs.org/en/download/
# Run installer → Accept defaults → Restart PowerShell

# Verify:
node --version    # Should show v20.x.x or newer
npm --version     # Should show 10.x.x or newer
```
- [ ] Node.js installed
- [ ] npm works

---

### Task 2: Install Rust
```powershell
# Download from: https://www.rust-lang.org/tools/install
# Run rustup-init.exe → Choose option 1 → Restart PowerShell

# Verify:
rustc --version   # Should show 1.75.0 or newer
cargo --version   # Should show 1.75.0 or newer
```
- [ ] Rust installed
- [ ] cargo works

---

### Task 3: Verify Python
```powershell
python --version  # Should show 3.12.0
```
- [x] Python 3.12.0 already installed ✅

---

## ☑️ Testing: Run the App

### Task 4: Install Dependencies
```powershell
cd C:\Users\aitor\audiovisual\audiovisuals\Code\desktop
npm install
```
- [ ] Dependencies installed successfully

---

### Task 5: Launch App
```powershell
npm run tauri dev
```

**Wait for:**
- Vite server starts
- Rust compiles (2-3 min first time)
- App window opens

- [ ] App launched successfully
- [ ] 5 tabs visible

---

### Task 6: Test Python Integration
1. Find "Test Python Integration" button (in Synesthesia tab)
2. Click it
3. Wait for result

**Expected:**
- Loading state shows
- Success message appears:
  ```
  Success: Yes
  Message: Python test completed with exit code: 0
  ```

- [ ] Button clicked
- [ ] Success message displayed

---

### Task 7: Check for Errors
1. Press F12 to open DevTools
2. Check Console tab for errors

- [ ] No red errors in console

---

## ☑️ Documentation

### Task 8: Fill in Results
```powershell
# Open in text editor:
Code\desktop\WEEK_2_RESULTS.md
```

- [ ] Documented versions installed
- [ ] Documented test results
- [ ] Noted any issues

---

## ✅ Week 2 Complete When:

- [ ] All toolchain installed (Node, Rust, Python)
- [ ] App launches successfully
- [ ] Python integration test passes
- [ ] Results documented
- [ ] No critical blockers

---

## 🆘 Troubleshooting Quick Reference

### Issue: `npm: command not found`
**Fix:** Restart PowerShell completely (close all windows)

### Issue: App won't launch
**Fix:** 
```powershell
cargo clean
npm run tauri dev
```

### Issue: Python test fails
**Fix:** 
```powershell
# Verify Python works:
python --version
python -c "print('Hello')"
```

### Issue: Compilation errors
**Fix:**
```powershell
rustup update
cargo clean
```

---

## 📞 Need Help?

1. Check `WEEK_1_COMPLETE.md` for architecture details
2. Check `WEEK_2_RESULTS.md` for what to document
3. Check `docs/Phase3-MVP/SETUP_GUIDE.md` for detailed setup

---

**Ready?** Start with Task 1 above! ⬆️


