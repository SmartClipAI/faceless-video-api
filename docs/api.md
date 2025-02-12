# API Design Document

## 1. Overview
This API provides video generation services and user authentication using JWT.

## 2. Base URL
```shell
https://api.example.com/v1
```

## 3. Authentication
This API uses JWT (JSON Web Tokens) for authentication. Include the JWT token in the Authorization header as a Bearer token for authenticated requests.

## 4. Endpoints

### 4.1 User Authentication

#### 4.1.1 Login for Access Token

##### Request

- **Method**: POST
- **URI**: `/auth/token`
- **Content-Type**: application/x-www-form-urlencoded

##### Request Body Parameters
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | User's username |
| password | string | Yes | User's password |

##### Response

###### Success Response
- **Status Code**: 200 OK
- **Content-Type**: application/json

```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

###### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| access_token | string | JWT access token |
| token_type | string | Type of the token (always "bearer") |

###### Error Response
- **Status Code**: 401 Unauthorized
- **Content-Type**: application/json

```json
{
    "detail": "Incorrect username or password"
}
```

#### 4.1.2 Refresh Token

##### Request

- **Method**: POST
- **URI**: `/auth/refresh`
- **Content-Type**: application/json

##### Headers
| Name | Required | Description |
|------|----------|-------------|
| Authorization | Yes | Bearer {token} |

##### Response

###### Success Response
- **Status Code**: 200 OK
- **Content-Type**: application/json

```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

###### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| access_token | string | New JWT access token |
| token_type | string | Type of the token (always "bearer") |

###### Error Response
- **Status Code**: 401 Unauthorized
- **Content-Type**: application/json

```json
{
    "detail": "Could not validate credentials"
}
```

### 4.2 Video Operations

#### 4.2.1 Generate Video

##### Request

- **Method**: POST
- **URI**: `/video`
- **Content-Type**: application/json
- **Authorization**: Bearer Token

##### Request Body
```json
{
    "story_topic": "string",
    "art_style": "string",
    "duration": "string",
    "language": "string",
    "voice_name": "string"
}
```

##### Parameters
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| story_topic | string | Yes | Topic for the story generation. Available options: "scary", "mystery", "bedtime", "interesting history", "urban legends", "motivational", "fun facts", "long form jokes", "life pro tips", "philosophy", "love", "custom topic" |
| art_style | string | Yes | Desired art style for generated images. Available options: "photorealistic", "cinematic", "anime", "comic-book", "pixar-art" |
| duration | string | Yes | Duration of the video. Available options: "short", "long" |
| language | string | Yes | Language for the video narration. Available options: "english", "czech", "danish", "dutch", "french", "german", "greek", "hindi", "indonesian", "italian", "chinese", "japanese", "norwegian", "polish", "portuguese", "russian", "spanish", "swedish", "turkish", "ukrainian" |
| voice_name | string | Yes | Name of the voice to use for narration. Available options: "alloy", "echo", "fable", "onyx", "nova", "shimmer" |

##### Response

###### Success Response
- **Status Code**: 200 OK
- **Content-Type**: application/json

```json
{
    "task_id": "string",
    "status": "string"
}
```

###### Error Response
- **Status Code**: 422 Unprocessable Entity
- **Content-Type**: application/json

```json
{
    "detail": "Validation error details"
}
```

#### 4.2.2 Get Video Task Status

##### Request

- **Method**: GET
- **URI**: `/video/tasks/{task_id}`
- **Authorization**: Bearer Token

##### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | string | The unique identifier of the video task |

##### Response

###### Success Response
- **Status Code**: 200 OK
- **Content-Type**: application/json

```json
{
    "task_id": "string",
    "status": "string",
    "progress": "number",
    "url": "string",
    "story_title": "string",
    "story_description": "string",
    "story_text": "string",
    "error_message": "string",
    "images": [
        {
            "id": "string",
            "status": "string",
            "urls": ["string"],
            "subtitles": "string",
            "created_at": "string",
            "updated_at": "string"
        }
    ],
    "created_at": "string",
    "updated_at": "string"
}
```

###### Error Response
- **Status Code**: 404 Not Found
- **Content-Type**: application/json

```json
{
    "detail": "Task not found"
}
```

### 4.3 Image Operations

#### 4.3.1 Get Image Task Status

##### Request

- **Method**: GET
- **URI**: `/images/tasks/{task_id}`
- **Authorization**: Bearer Token

##### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | string | The unique identifier of the image task |

##### Response

###### Success Response
- **Status Code**: 200 OK
- **Content-Type**: application/json

```json
{
    "task_id": "string",
    "status": "string",
    "created_at": "string",
    "updated_at": "string",
    "story_text": "string",
    "images": [
        {
            "id": "string",
            "status": "string",
            "urls": ["string"],
            "subtitles": "string",
            "created_at": "string",
            "updated_at": "string"
        }
    ]
}
```

###### Error Response
- **Status Code**: 404 Not Found
- **Content-Type**: application/json

```json
{
    "detail": "Task not found"
}
```

#### 4.3.2 Regenerate Image

##### Request

- **Method**: POST
- **URI**: `/images/{image_id}`
- **Authorization**: Bearer Token

##### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| image_id | string | The unique identifier of the image to regenerate |

##### Response

###### Success Response
- **Status Code**: 200 OK
- **Content-Type**: application/json

```json
{
    "task_id": "string",
    "status": "string",
    "urls": ["string"],
    "created_at": "string",
    "updated_at": "string"
}
```

###### Error Response
- **Status Code**: 404 Not Found
- **Content-Type**: application/json

```json
{
    "detail": "Image not found"
}
```