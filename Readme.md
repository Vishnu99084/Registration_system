# Registration System — DATA & Project README

This repository contains a sample **DATA** object (countries → states → cities) used by a Registration System project. The dataset is stored in a JavaScript file and used by front-end components (forms, dropdowns) or simple demo pages.

---

## Table of Contents

1. Project overview
2. Prerequisites
3. Project structure
4. Quick start — run locally
5. How to use the `DATA` object
6. How to edit / extend countries, states, cities
7. Running tests (suggested)
8. Contributing
9. Troubleshooting
10. License

---

## 1. Project overview

This project demonstrates a hierarchical `DATA` object used to populate country/state/city dropdowns in a registration form. The data includes multiple countries and expanded Indian states with 10 cities each. The project is intentionally simple so it can be used as a demo, learning exercise, or starting point for larger applications.

## 2. Prerequisites

* Node.js (optional — only required if you want to run a local static server or tests)
* A web browser (Chrome/Firefox)
* A code editor (VS Code recommended)

## 3. Project structure

```
project-root/
├─ data.js            # Contains the `DATA` constant (countries, states, cities)
├─ index.html         # Demo page that uses DATA to populate dropdowns
├─ app.js             # Demo JS logic for dropdown population & validation
├─ styles.css         # Optional styles
├─ tests/             # (Optional) Unit or integration tests
└─ README.md          # This file
```

## 4. Quick start — run locally

**Option A: Open in browser (no server required)**

1. Open `index.html` directly in your browser.
2. The demo page should load and populate country/state/city dropdowns from `data.js`.

**Option B: Run a local static server (recommended for AJAX or module usage)**

* Using Node (http-server):

  ```bash
  npm install -g http-server
  http-server . -p 8080
  # Open http://localhost:8080
  ```
* Or using Python 3:

  ```bash
  python -m http.server 8080
  # Open http://localhost:8080
  ```

## 5. How to use the `DATA` object

* `DATA.countries` is an array of country objects:

  ```js
  {
    code: "IN",
    name: "India",
    phoneCode: "+91",
    states: [ { name: "Telangana", cities: ["Hyderabad", "Warangal", ...] }, ... ]
  }
  ```
* To populate a country dropdown: iterate `DATA.countries` and use `country.name`.
* For states: find the selected country by `code` or `name`, then read `country.states`.
* For cities: read `state.cities`.

## 6. How to edit / extend countries, states, cities

1. Open `data.js` in your editor.
2. Find the `DATA` constant and add/modify country objects.
3. Follow the existing structure: each country has a `code`, `name`, `phoneCode`, and `states` array.
4. Each `state` should have `name` and `cities` array with strings.

**Best practices:**

* Keep country `code` as ISO-style short code (e.g. `IN`, `US`).
* Avoid duplicate city names within the same state.
* If adding many entries, consider splitting data into multiple JSON files and load lazily.

## 7. Running tests (suggested)

This project does not include a formal test suite by default. Suggested tests:

* **Unit tests**: verify functions that map country → states and state → cities (use Jest or pytest if using Python).
* **Integration tests**: run the demo page and assert dropdowns update correctly (use Playwright or Cypress).
* **Load test**: create a large synthetic dataset and measure time to populate dropdowns.

**Example (Node + Jest)**

```bash
npm init -y
npm install --save-dev jest
# Create tests/country.test.js that imports data.js and asserts counts
npx jest
```

## 8. Contributing

* Fork the repo and create a feature branch.
* Add tests for any behavioral changes.
* Keep changes focused and make small PRs.
* Use semantic commit messages and include a short description in the PR.

## 9. Troubleshooting

* If dropdowns are empty, check console for errors and ensure `data.js` is loaded before `app.js`.
* If the page is served as modules, ensure CORS or server settings allow the files to be fetched.
* Large `DATA` objects can slow down initial rendering; use lazy-loading or pagination for very large lists.

## 10. License

This example is provided under the MIT License — adapt freely for demos and learning.

---

If you want, I can also:

* Generate a sample `index.html` + `app.js` to show how to use `DATA`.
* Add Jest or Playwright test templates.
* Export `DATA` as `data.json` and show lazy-loading code.

Tell me which of the above you want next.
