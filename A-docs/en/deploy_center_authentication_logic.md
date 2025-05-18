# Deploy Center Login Authentication Documentation

## Introduction

Deploy Center login uses username + password authentication. When the system enables two-factor authentication (2FA), users are required to additionally enter a dynamic verification code to verify their identity, ensuring account security. It supports dynamic re-binding of the authenticator to handle situations such as device loss or code expiration.

> You can bind common 2FA authenticators such as **Microsoft Authenticator**, **Google Authenticator**, **Aliyun App**, or other apps supporting the TOTP protocol.

---

## Login Logic Flowchart

```mermaid
graph TD
    A[User enters username and password] --> B{Is 2FA enabled in the system?}
    B -- No --> C[Call /api/deploy-center/auth/login endpoint, login succeeds, return token]
    B -- Yes --> D[Call /api/deploy-center/2fa/status to check if user has bound an authenticator]

    D -- No --> E[Pop up 2FA binding dialog]
    E --> F[Call /api/deploy-center/2fa/setup to get QR code]
    F --> G[Display QR code, prompt user to bind]
    G --> H[User completes scan and clicks "I have bound"]
    H --> I[Close 2FA binding dialog]
    I --> K

    D -- Yes --> J[Pop up verification code input dialog]

    J --> K[User enters verification code]
    J --> L[User can click "Rebind Authenticator"]
    L --> F

    K --> M[Call /api/deploy-center/auth/login with verification code, login succeeds, return token]
```

---

## API Specifications

### Login Endpoint `/api/deploy-center/auth/login`

**Method**: POST

**Request Parameters**:

```json
{
  "identifier": "username",
  "credential": "password",
  "two_factor_code": "verification code (optional)"
}
```

**Note**: If 2FA is enabled and the user has bound an authenticator, the `two_factor_code` is required. Otherwise, the system will prompt missing or incorrect verification code.

---

### Query Binding Status `/api/deploy-center/2fa/status`

**Method**: GET

**Request Parameters**:

```query
username=alice
```

**Response Example**:

```json
{
  "code": 200,
  "status": "success",
  "msg": null,
  "data": true
}
```

---

### Get QR Code `/api/deploy-center/2fa/setup`

**Method**: POST

**Request Parameters**:

```json
{
  "username": "alice"
}
```

**Response Example**:

```json
{
  "code": 200,
  "status": "success",
  "msg": null,
  "data": {
    "secret": "ASFASFASFASFASF",
    "qr_code_base64": "data:image/png;base64,..."
  }
}
```

**Note**: Users who have already bound can also rebind (overwrite the old secret). The frontend calls this endpoint through the "Rebind Authenticator" option.

---

### Verify Code `/api/deploy-center/2fa/verify`

**Method**: POST

**Request Parameters**:

```json
{
  "username": "alice",
  "code": "123456"
}
```

**Response Example**:

```json
{
  "code": 200,
  "status": "success",
  "msg": null,
  "data": true
}
```

**Note**: After scanning and binding, this endpoint can be used to verify if the user input code is correct.

---

## Frontend Design Key Points

- On first login, check if 2FA is enabled and whether the user has bound an authenticator
- If not bound: call `/api/deploy-center/2fa/setup` to get the QR code for binding
- If bound: pop up verification code input dialog
- Provide an underlined "Rebind Authenticator" button in the dialog to guide the user to regenerate the QR code (calls `/setup` again)
- Login completes as long as the verification code is correct

---

## Security Recommendations

- Add rate limiting on the `/setup` endpoint to prevent brute-force QR code refresh
- Record binding timestamp, e.g., `two_factor_bound_at`
- Recommend requiring the user to verify their password at least once before "Rebinding Authenticator" (for enhanced security)

---

## Summary

Deploy Center login authentication features:

- Supports system-level enabling/disabling of 2FA
- Users can bind a 2FA authenticator after their first login
- Supports self-service re-binding on verification failure
- Clear login flow, well-designed APIs, easy to extend