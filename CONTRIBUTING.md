# Contributing to Spendable 💡

Thank you for your interest in contributing to **Spendable**! We welcome contributions, bug reports, feature requests, and documentation improvements.

---

## 🚀 Quick Setup

### 1. Fork & Clone
```bash
git clone https://github.com/Supan-Roy/Spendable.git
cd Spendable
```

### 2. Environment Setup
```bash
# Create Python Virtual Environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Install Backend Dependencies
pip install -r backend/requirements.txt

# Install Frontend & Workspace Dependencies
pnpm install
```

### 3. Run Development Server
```bash
pnpm run dev
```

### 4. Run Tests
```bash
pnpm test
```

---

## 📋 How to Contribute

### Reporting Bugs
Before opening a bug report, please search existing issues. If not found, open an issue using the **Bug Report** template including:
- Operating System & browser version
- Steps to reproduce
- Expected vs. actual behavior
- Terminal logs or screenshots if applicable

### Proposing Features
Feature requests are welcome! Use the **Feature Request** template to outline:
- Problem the feature solves
- Proposed user experience or technical implementation
- Any alternative solutions considered

### Submitting Pull Requests
1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Write clean, readable code and maintain formatting.
3. Ensure backend unit tests pass:
   ```bash
   pnpm test
   ```
4. Ensure frontend builds cleanly:
   ```bash
   pnpm --prefix frontend build
   ```
5. Submit your Pull Request targeting `main` using the PR template.

---

## 🛡️ Coding Standards & Principles

- **No Fake Data**: Do not hardcode fictional financial figures into user interfaces or test fixtures without explicit classification.
- **LLM vs Financial Engine Separation**: Keep mathematical/analytical logic separate from natural language explanation layers.
- **Data Honesty**: Preserve explicit boundaries between `OBSERVED`, `INFERRED`, and `PREDICTED` data.
