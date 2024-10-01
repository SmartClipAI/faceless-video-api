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

#### 4.1.1 Login

##### Request

- **Method**: POST
- **URI**: `/auth/sessions`
- **Content-Type**: application/json

##### Request Body

```json
{
    "username": "string",
    "password": "string"
}
```


##### Parameters
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
    "error": "Incorrect username or password"
}
```

#### Example

###### Request Example

```shell
curl -X POST https://api.example.com/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{
        "username": "superuser",
        "password": "superuserpassword"
    }'
```

##### Response Example

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
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
    "error": "Could not validate credentials"
}
```

##### Example

###### Request Example

```shell
curl -X POST https://api.example.com/v1/auth/refresh \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

###### Response Example

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### 4.2 Image Generation

#### 4.2.1 Generate Story Images

Creates a new image generation task based on a story generated from the provided topic and art style.

##### Request

- **Method**: POST
- **URI**: `/images`
- **Content-Type**: application/json
- **Authorization**: Bearer Token

##### Headers

| Name | Required | Description |
| ---- | -------- | ----------- |
| Authorization | Yes | Bearer {token} |

##### Request Body

```json
{
    "story_topic": "string",
    "art_style": "string"
}
```

##### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| story_topic | string | Yes | The topic or theme for story generation and subsequent image creation |
| art_style | string | Yes | The desired art style for the generated images |

##### Response

###### Success Response
- **Status Code**: 202 Accepted
- **Content-Type**: application/json

```json
{
    "task_id": "string",
    "created_at": "string",
    "status_url": "string"
}
```

###### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| task_id | string | Unique identifier for the story image generation task |
| created_at | string | ISO 8601 timestamp of when the task was created |
| status_url | string | URL for checking the task status and retrieving results |

###### Error Response
- **Status Code**: 400 Bad Request
- **Content-Type**: application/json


```json
{
    "error": "Invalid input parameters",
    "details": {
        "art_style": "Unsupported art style"
    }
}
```

##### Example

###### Request Example

```shell
curl -X POST https://api.example.com/v1/images \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
    -d '{
        "story_topic": "A time traveler's first day in ancient Rome",
        "art_style": "photorealistic"
    }'
```

###### Response Example

```json
{
    "task_id": "task_7890xyz",
    "created_at": "2023-04-01T12:00:00Z",
    "status_url": "/images/tasks/task_7890xyz"
}
```


#### 4.2.2 Get Story Image Generation Task Status

Retrieves the status of a specific story image generation task, including the story text and URLs of generated images if completed.

##### Request

- **Method**: GET
- **URI**: `/images/tasks/{task_id}`
- **Authorization**: Bearer Token

##### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | string | The unique identifier of the story image generation task |

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
            "url": "string",
            "subtitles": "string"
        }
    ]
}
```


###### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| task_id | string | Unique identifier for the story image generation task |
| status | string | Current status of the task (e.g., "queued", "processing", "completed", "failed") |
| created_at | string | ISO 8601 timestamp of when the task was created |
| updated_at | string | ISO 8601 timestamp of when the task was updated |
| story_text | string | The generated story text (null if not completed) |
| images | array | List of generated images (empty if not completed) |
| images[].id | string | Unique identifier for each generated image |
| images[].status | string | Status of the individual image (e.g., "processing", "completed", "failed") |
| images[].urls | string | List of URL of the generated image |
| images[].subtitles | string | Subtitles or description for the image |

###### Error Response
- **Status Code**: 404 Not Found
- **Content-Type**: application/json

```json
{
    "error": "Story image generation task not found"
}
```

##### Example

###### Request Example

```shell
curl -X GET https://api.example.com/v1/images/tasks/task_7890xyz \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

###### Response Example

```json
{
    "task_id": "task_7890xyz",
    "status": "processing",
    "created_at": "2023-04-01T12:00:00Z",
    "updated_at": "2023-04-01T12:15:30Z",
    "story_text": "As the swirling mists of time cleared, Marcus found himself standing in the bustling heart of ancient Rome...",
    "images": [
        {
            "id": "img_001abc",
            "status": "completed",
            "url": "https://example.com/generated_images/img_001abc.jpg",
            "subtitles": "A time traveler materializes in the Roman Forum"
        },
        {
            "id": "img_002def",
            "status": "completed",
            "url": "https://example.com/generated_images/img_002def.jpg",
            "subtitles": "Marcus marvels at the grandeur of the Colosseum"
        },
        {
            "id": "img_003ghi",
            "status": "processing",
            "url": "https://example.com/generated_images/img_003ghi.jpg",
            "subtitles": "An encounter with a Roman centurion"
        }
    ]
}
```

#### 4.2.3 Regenerate Specific Image

Requests the regeneration of a specific image within a completed image generation task.

##### Request

- **Method**: POST
- **URI**: `/images/{image_id}`
- **Content-Type**: application/json
- **Authorization**: Bearer Token

##### Path Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| image_id | string | Unique identifier for the image to be recreated |


##### Headers

| Name | Required | Description |
| ---- | -------- | ----------- |
| Authorization | Yes | Bearer {token} |

##### Request Body

No request body is required for this endpoint.


##### Response

###### Success Response
- **Status Code**: 202 Accepted
- **Content-Type**: application/json

```json
{
    "id": "string",
    "status": "string",
    "urls": "list",
    "created_at": "string",
    "updated_at": "string"
}

###### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier of the original image |
| status | string |  Status of the image (e.g., "processing", "completed", "failed") |
| urls | string | List of URL of the regenerated image |
| created_at | string | ISO 8601 timestamp of when the regeneration task was created |
| updated_at | string | ISO 8601 timestamp of when the regeneration task was updated |


###### Error Response

- **Status Code**: 200 OK
- **Content-Type**: application/json

```json
{
    "error": "Image not found"
}
```

##### Example

###### Request Example

```shell
curl -X POST https://api.example.com/v1/images/img_003ghi \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

###### Response Example

```json
{
    "task_id": "task_7890xyz",
    "url": "/images/img_003ghi",
    "status": "completed", 
    "created_at": "2024-09-28T00:05:36.865510Z", 
    "updated_at": "2024-09-28T06:36:17.891279Z"
}
```

#### 4.2.4 Get Specific Image Status

Retrieves the status of a specific image within an image generation task.

##### Request

- **Method**: GET
- **URI**: `/images/{image_id}`
- **Authorization**: Bearer Token

##### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| image_id | string | The unique identifier of the image |
##### Response

###### Success Response
- **Status Code**: 200 OK
- **Content-Type**: application/json

```json
{
    "image_id": "string",
    "urls": "list",
    "subtitles": "string",
    "status": "string",
    "created_at": "string",
    "updated_at": "string"
}
```

###### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| image_id | string | Unique identifier of the image |
| task_id | string | Unique identifier for the image generation task |
| urls | string | List of URL of the generated image |
| subtitles | string | Subtitles or description for the image |
| status | string | Status of the image (e.g., "completed", "regenerating", "failed") |
| created_at | string | ISO 8601 timestamp of when the image was first created |
| updated_at | string | ISO 8601 timestamp of when the image was last updated |

###### Error Response
- **Status Code**: 404 Not Found
- **Content-Type**: application/json

```json
{
    "error": "Image not found"
}
```

##### Example

###### Request Example

```shell
curl -X GET https://api.example.com/v1/images/img_003ghi/tasks/task_7890xyz/status \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

###### Response Example

```json
{
    "image_id": "img_003ghi",
    "task_id": "task_7890xyz",
    "urls": ["https://example.com/generated_images/img_003ghi.jpg"],
    "subtitles": "A time traveler materializes in the Roman Forum",
    "status": "completed",
    "created_at": "2023-04-01T12:00:00Z",
    "updated_at": "2023-04-01T12:15:30Z"
}
```