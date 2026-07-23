# Project Handover Document - PCMC Assessment System

This document summarizes the changes and enhancements made to the PCMC site, specifically focusing on the assessment system and content structure.

## 1. Core Objectives
- Modernize the assessment system to support image-based questions and options.
- Harmonize the project structure with a `Subject` -> `Standard` -> `Topic` hierarchy.
- Provide a robust Excel (.xlsx) upload mechanism for questions with embedded images.
- Improve the user experience with an AJAX-powered, non-flickering assessment modal.

---

## 2. Backend & Model Changes

### Model Updates (`pcmc_app/models.py`)
- **`Question`**: Added `ImageField`s for the question text and all four options (`question_image`, `option{1-4}_image`). These are optional; the system falls back to text if images are missing.
- **New Hierarchy**: Introduced `Subject`, `Standard`, and `Topic` models to replace/augment legacy flat structures.
- **`StudyMaterial`**: Added a model for PDF documents linked to `Topic`.

### Admin Logic (`pcmc_app/admin.py`)
- **Excel (.xlsx) Import**: Implemented a custom import view that uses `openpyxl` to extract images embedded in Excel cells.
- **Backward Compatibility**: Maintained the existing CSV upload logic for text-only questions.
- **Mapping**: Excel columns map to question text, options, correct option index, and optional reason.

---

## 3. Frontend & UI Enhancements

### Assessment Template (`pcmc_app/templates/assessment/question.html`)
- **Conditional Rendering**: Displays images for questions/options if available; otherwise displays text.
- **AJAX Navigation**: Use of jQuery and `DOMParser` to update only the assessment card content, preventing page reloads and flickering.
- **Immediate Feedback**: Correct (Green) and Incorrect (Red) styling applied immediately after submission.
- **Feedback Images**: If a question is image-based, the "Correct Answer" feedback now displays the correct image instead of empty text.

### Modal Implementation
- The assessment is now launched in a centered Bootstrap modal (`iframe`) from the Science/Math subpages.
- Added a `?popup=true` parameter to the URL to hide the header and footer when inside the modal.

---

## 4. Critical Bug Fixes

### Template Syntax Issues
- Resolved a persistent `TemplateSyntaxError` caused by:
    - Missing spaces around the `==` operator in Django tags (e.g., `{% if x == 1 %}`).
    - Newlines/breaks within `<input>` tags that split Django `{% if %}` blocks.
- **Resolution**: The `question.html` file was meticulously rewritten to keep logic on single lines and use strict spacing.

### Content Display
- Fixed "missing feedback text" for image-only questions by passing the correct option's image URL in the feedback context.

---

## 5. Technical Details & Dependencies

### New Dependencies
- `openpyxl`: Required for parsing `.xlsx` files and extracting images.
- `Pillow`: Required for handling `ImageField` operations in Django.

### Important Files
- `pcmc_app/templates/assessment/question.html`: Core assessment logic and UI.
- `pcmc_app/admin.py`: Contains the `QuestionAdmin` logic for file imports.
- `pcmc_app/views.py`: Handles the assessment flow, session management, and feedback logic.

### Commands for New Setup
```bash
pip install openpyxl Pillow
python manage.py makemigrations
python manage.py migrate
```

---

## 6. Verification Steps
- [x] Upload `.xlsx` file with images in Admin -> Questions.
- [x] Launch assessment via "Take Assessment" button in Science/Math pages.
- [x] Submit wrong answer and verify red feedback with correct answer image.
- [x] Click "Next Question" and verify smooth AJAX transition.
