# Testing & Quality Assurance Report

**Course:** CSCD602: Advanced Software Engineering  
**Institution:** University of Ghana, Department of Computer Science  
**Project:** StudyPlanner Application  
**Author:** [Your Full Name] (Student ID: [Your Student ID])  

---

## 1. Executive Summary

This report documents the testing methodology, test case execution matrix, defect remediation log, and quality assurance metrics for the **StudyPlanner** application. Testing was conducted across Unit, Integration, Functional, Security, and Usability dimensions to ensure production readiness.

---

## 2. Test Execution Summary

- **Total Test Cases Executed**: 9 (Automated Pytest) + 5 (Manual Functional Verification)
- **Passed**: 14
- **Failed**: 0
- **Pass Rate**: **100%**
- **Test Framework**: `pytest 7.4.0` with in-memory SQLite database context.

---

## 3. Automated Test Execution Matrix (Pytest Suite)

| Test ID | Test Category | Target Function / Endpoint | Scenario Description | Expected Result | Actual Result | Status |
|:---|:---|:---|:---|:---|:---|:---|
| **TC-01** | Unit | `User.set_password()` | Password hashing and verification check (`check_password`). | Password hash stored securely; correct password returns `True`; wrong password returns `False`. | Worked as expected. | **PASS** |
| **TC-02** | Unit | `Task.get_priority_color()` | Priority tag CSS class resolution for High priority. | Returns `"priority-high"`. | Returns `"priority-high"`. | **PASS** |
| **TC-03** | Unit | `Task.formatted_study_time()` | Format 3665 seconds into `HH:MM:SS` string. | Returns `"01:01:05"`. | Returns `"01:01:05"`. | **PASS** |
| **TC-04** | Unit | `Session.stop()` | Calculate duration between start and stop timestamps. | Returns positive duration integer $\ge 10$ seconds. | Duration calculated accurately. | **PASS** |
| **TC-05** | Functional | `GET /`, `GET /about`, `GET /health` | Public routes rendering and system health check status. | Public pages return HTTP `200`; `/health` returns JSON `{"status": "healthy"}`. | HTTP 200 OK & JSON payload validated. | **PASS** |
| **TC-06** | Integration | `POST /login`, `GET /logout` | Authenticate existing user with valid password and terminate session. | Successful login redirects to dashboard; logout flashes success notification. | Redirected to dashboard; flash message displayed. | **PASS** |
| **TC-07** | Integration | `POST /task/new`, `POST /task/<id>/edit`, `POST /task/<id>/delete` | Complete CRUD cycle for a study task. | Task created in DB, updated, and deleted cleanly. | Database records updated and deleted as expected. | **PASS** |
| **TC-08** | Integration | `POST /task/<id>/timer/start`, `POST /task/<id>/timer/stop` | REST API study timer stopwatch logging. | JSON response `{"success": true}`; task total study time updated. | JSON success response; study time incremented. | **PASS** |
| **TC-09** | Unit / Form | `RegisterForm` Validation | Attempt registration with duplicate username or email. | Validation fails (`validate() == False`); error messages attached to form fields. | Field error attached correctly. | **PASS** |

---

## 4. Defect Log & Remediation

During initial test execution, two minor defects were identified and immediately remediated:

| Defect ID | Component | Root Cause | Severity | Corrective Action Taken | Status |
|:---|:---|:---|:---|:---|:---|
| **DEF-01** | `app.py` | `Flask-Limiter` instance local variable was garbage-collected between requests during Pytest client execution. | High | Attached `limiter` instance explicitly to Flask app object (`app.limiter = limiter`). | **Resolved** |
| **DEF-02** | `tests/test_forms.py` | Mismatched string assertion for duplicate username message. | Low | Aligned test assertion string with form validator text: `"Username is already taken. Please choose another."`. | **Resolved** |

---

## 5. Security & Usability Verification

### 5.1 Security Testing
- **SQL Injection**: Verified all database queries utilize SQLAlchemy parameterized statements. Attempted `' OR 1=1 --` input in search field; query safely escaped without syntax errors.
- **CSRF Protection**: Verified that form submissions lacking `csrf_token` return HTTP `400 Bad Request`.
- **Rate Limiting**: Tested brute-force login attempts exceeding 15 requests/hour; system returned HTTP `429 Rate Limit Exceeded`.

### 5.2 Usability & Responsiveness Testing
- Verified dynamic navigation toggle on viewports $< 768\text{px}$.
- Confirmed responsive card layout adjustment across mobile, tablet, and desktop screens.
