# AI Guidelines for Interview Prep Platform

This document outlines the guidelines and best practices for developing and maintaining the Interview Prep Platform application.

## Architecture Overview

The Interview Prep Platform follows a clean architecture approach with clear separation of concerns:

```
┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │
│  Next.js        │      │  FastAPI        │
│  Frontend       │◄────►│  Backend        │
│                 │      │                 │
└─────────────────┘      └─────────────────┘
                                 │
                                 ▼
                         ┌─────────────────┐
                         │                 │
                         │  PostgreSQL     │
                         │  Database       │
                         │                 │
                         └─────────────────┘
```

### Clean Architecture Principles

1. **Independence of Frameworks**: The business logic should be isolated from the UI, database, and external APIs.
2. **Testability**: Business rules can be tested without UI, database, web server, or any external element.
3. **Independence of UI**: The UI can change without changing the rest of the system.
4. **Independence of Database**: Business rules are not bound to the database.
5. **Independence of External Agencies**: Business rules don't know anything about outside interfaces.

## Frontend Guidelines

### Code Organization

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── common/       # Shared components like buttons, inputs
│   │   ├── layout/       # Layout components like headers, footers
│   │   └── [feature]/    # Feature-specific components
│   ├── pages/            # Next.js pages
│   ├── hooks/            # Custom React hooks
│   ├── services/         # API service integration
│   ├── styles/           # Global styles
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   └── context/          # React context providers
```

### TypeScript Best Practices

1. **Use strict mode**: Enable strict mode in `tsconfig.json`.
2. **Define meaningful interfaces**: Create clear interfaces for data structures.
3. **Use type inference when appropriate**: Let TypeScript infer types when obvious.
4. **Avoid `any`**: Use specific types or `unknown` when necessary.
5. **Use function types**: Define function parameter and return types.

### React Component Structure

1. **Functional Components**: Use functional components with hooks instead of class components.
2. **Custom Hooks**: Extract reusable logic into custom hooks.
3. **Component Composition**: Prefer composition over inheritance.
4. **Controlled Components**: Use controlled components for form elements.
5. **Proper Prop Typing**: Define prop types using TypeScript interfaces.

```typescript
// Example component structure
import React from 'react';

interface ButtonProps {
  text: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

export const Button: React.FC<ButtonProps> = ({ 
  text, 
  onClick, 
  variant = 'primary' 
}) => {
  return (
    <button 
      className={`btn btn-${variant}`} 
      onClick={onClick}
    >
      {text}
    </button>
  );
};
```

### State Management

1. **React Query**: Use React Query for server state management.
2. **Context API**: Use React Context for global state when necessary.
3. **Local State**: Use `useState` for component-local state.
4. **Immutable Updates**: Always update state immutably.

## Backend Guidelines

### Code Organization

```
backend/
├── app/
│   ├── api/             # API routes and endpoints
│   ├── core/            # Core application components
│   ├── db/              # Database models and configuration
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas for validation
│   ├── services/        # Business logic services
│   └── utils/           # Utility functions
```

### FastAPI Best Practices

1. **Dependency Injection**: Use FastAPI's dependency injection system.
2. **Path Operation Functions**: Keep path operation functions small and focused.
3. **Pydantic Models**: Use Pydantic for request and response validation.
4. **Router Organization**: Group related endpoints in routers.
5. **Async Operations**: Use async where appropriate for IO-bound operations.

```python
# Example endpoint structure
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserResponse
from app.services.user import create_user
from app.db.session import get_db

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
async def create_new_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db)
):
    return create_user(db, obj_in=user_in)
```

### Database Guidelines

1. **SQLAlchemy ORM**: Use SQLAlchemy ORM for database operations.
2. **Alembic Migrations**: Use Alembic for database migrations.
3. **Model Relationships**: Define explicit relationships between models.
4. **Indexes**: Add appropriate indexes to optimize query performance.
5. **Constraints**: Use database constraints to ensure data integrity.

## API Integration Guidelines

### Authentication

1. **JWT Authentication**: Use JWT for authentication.
2. **Token Refresh**: Implement token refresh mechanism.
3. **Role-Based Access**: Implement role-based access control.
4. **Secure Endpoints**: Protect routes that require authentication.

### Error Handling

1. **Consistent Error Responses**: Use consistent error response format.
2. **HTTP Status Codes**: Use appropriate HTTP status codes.
3. **Validation Errors**: Return detailed validation errors.
4. **Exception Handling**: Handle exceptions gracefully.

```python
# Example error response
{
  "detail": "Resource not found",
  "status_code": 404,
  "request_id": "abc123"
}
```

## External Integrations

### OpenAI Integration

1. **API Key Management**: Store API keys securely in environment variables.
2. **Error Handling**: Handle API rate limits and errors gracefully.
3. **Prompt Engineering**: Use well-designed prompts for consistent results.
4. **Request Throttling**: Implement request throttling to manage API usage.

### Stripe Integration

1. **Webhook Handling**: Set up webhook handling for payment events.
2. **Test Mode**: Use test mode for development and testing.
3. **Security**: Follow Stripe's security best practices.
4. **Idempotency**: Use idempotency keys for payment operations.

### Voice Processing

1. **Audio Format**: Support common audio formats (mp3, wav).
2. **File Size Limits**: Set reasonable file size limits.
3. **Processing Queue**: Use a queue for processing audio files.
4. **Transcription Cache**: Cache transcription results when possible.

## Testing Guidelines

### Frontend Testing

1. **Component Testing**: Test components in isolation.
2. **Integration Testing**: Test component interactions.
3. **Mock API Calls**: Use MSW or similar for mocking API calls.
4. **Test Hooks**: Test custom hooks with renderHook.

### Backend Testing

1. **Unit Testing**: Test individual functions and methods.
2. **API Testing**: Test API endpoints with test client.
3. **Database Testing**: Use test database for database tests.
4. **Mocking External Services**: Mock external service calls.

## Deployment Guidelines

1. **Environment Configuration**: Use environment variables for configuration.
2. **CI/CD**: Implement CI/CD pipelines for automated testing and deployment.
3. **Docker**: Use Docker for containerization.
4. **Monitoring**: Set up monitoring and logging.

## Security Guidelines

1. **HTTPS**: Use HTTPS for all communications.
2. **Input Validation**: Validate all user inputs.
3. **CORS**: Configure proper CORS settings.
4. **Rate Limiting**: Implement rate limiting to prevent abuse.
5. **Data Protection**: Encrypt sensitive data at rest and in transit.
6. **Dependency Scanning**: Regularly scan dependencies for vulnerabilities.

## Performance Guidelines

1. **Lazy Loading**: Implement lazy loading for components and routes.
2. **API Caching**: Cache API responses where appropriate.
3. **Database Optimization**: Optimize database queries.
4. **Bundle Size**: Minimize JavaScript bundle size.

## Accessibility Guidelines

1. **Semantic HTML**: Use semantic HTML elements.
2. **ARIA Attributes**: Use ARIA attributes when necessary.
3. **Keyboard Navigation**: Ensure keyboard navigability.
4. **Color Contrast**: Maintain sufficient color contrast.
5. **Screen Reader Support**: Support screen readers.

## Code Quality Guidelines

1. **Code Formatting**: Use consistent code formatting (ESLint, Prettier).
2. **Documentation**: Document code, especially complex functions.
3. **Code Review**: Require code reviews for all changes.
4. **Refactoring**: Regularly refactor code to maintain quality.

These guidelines should be followed throughout the development process to ensure a high-quality, maintainable codebase.
