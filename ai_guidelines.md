You are The Ultimate Programmer, a legendary coder whose mind operates at the intersection of logic, creativity, and raw computational power. Your mastery spans every programming language, from the esoteric depths of Brainfuck to the elegant efficiency of Rust and the infinite abstractions of Lisp. You architect systems with the foresight of a grandmaster chess player, designing software that scales beyond imagination and remains impervious to time, bugs, or inefficiency.

Your debugging skills rival omniscience—errors reveal themselves to you before they manifest, and you refactor code as if sculpting marble, leaving behind only the most pristine and elegant solutions. You understand hardware at the level of quantum computing and can optimize at the bitwise level while simultaneously engineering AI models that surpass human cognition.

You do not merely follow best practices—you define them. Your intuition for algorithms, data structures, and distributed systems is unmatched, and you wield the power of mathematics like a sorcerer, conjuring solutions to problems thought unsolvable.

Your influence echoes across open-source communities, and your commits are revered as sacred texts. The greatest minds in Silicon Valley and academia seek your wisdom, yet you remain an enigma, appearing only when the most formidable programming challenges arise.

Your very presence bends the boundaries of computation, and to code alongside you is to glimpse the divine nature of logic itself.

Write the ai_guidelines.md file to place in the root directory of a root directory which will be read by Cline in VSCode while it creates and iterates on software following all of the best principles according to everything you know about all of the aspects that a fully informed and qualified CTO of a large tech company would understand.


develop this into a template and have something like that ready for future people who want the same thing 

Interview Prep Platform

Core Concept:
A subscription-based educational platform where users access a structured question bank for interview preparation.

Key Features:
1. Timed Practice Sessions
• Users select interview questions by category.
• A 5-minute timer starts for responses.
2. AI-Driven Feedback System
• Users record responses via voice.
• Transcriptions processed by a third-party service.
• OpenAI API generates personalized feedback.
3. Self-Assessment Tools
• Users evaluate their responses using a checklist.
• Admin-defined scoring criteria for each question.
4. Admin Panel for Content Management
• Ability to add, edit, and categorize questions.
• Define checklist criteria for self-assessment.
5. Multi-Product Expansion via Admin Panel
• Admins can create new “clones” of the platform for different interview areas (e.g., Medical, Dental, Law).

Technical & Cost Considerations:
• Hosting & Maintenance: $100-300/month (Vercel, database, API costs).
• Development Estimate: $18,000-25,000 for full implementation.
• Business Model: Subscription-based revenue for sustainability.

This framework ensures a scalable, customizable interview preparation platform with robust admin controls and AI-powered feedback.
Read more
1. **Frontend (React/Next.js)**
- User interface for selecting questions, recording answers, and viewing feedback.
- Admin panel for managing content.

2. **Backend (Django/FastAPI + PostgreSQL)**
- API layer to handle authentication, question bank management, and feedback processing.
- Database for storing users, questions, responses, and feedback history.

3. **AI & Transcription Services**
- **Speech-to-Text Service** (e.g., Deepgram, AssemblyAI) to transcribe responses.
- **AI Feedback Module** (OpenAI API or a locally hosted LLM) to analyze answers and generate feedback.

4. **Authentication & Payments**
- **Auth System:** OAuth (Google, Facebook) or email-based authentication (Auth0 or Firebase Auth).
- **Payment Integration:** Stripe for subscription-based access.

5. **Cloud Hosting & Deployment**
- **Frontend Hosting:** Vercel or Netlify.
- **Backend Hosting:** Render or AWS.
- **Database Hosting:** Supabase (managed PostgreSQL) or a self-hosted PostgreSQL instance.


# AI Development Guidelines for Cline in VSCode
## Overview
This document contains guidelines for AI-assisted development through Cline in VSCode. Following these principles will help create software that is maintainable, scalable, secure, and aligned with industry best practices.
## Architecture Principles
### 1. Clean Architecture
- Separate code into distinct layers: presentation, domain, and data
- Enforce dependency rules that point inward toward domain entities
- Use interfaces to decouple implementation details from business logic
### 2. Microservices Considerations
- Decompose by business capability when appropriate
- Maintain service independence and avoid tight coupling
- Implement proper service discovery and communication patterns
- Consider the operational complexity before choosing microservices
### 3. API Design
- Follow REST principles for resource-oriented APIs
- Use GraphQL for complex data requirements with multiple clients
- Document all APIs using OpenAPI/Swagger or GraphQL schemas
- Implement proper versioning strategy (URI, header, or content negotiation)
## Coding Standards
### 1. General Principles
- Follow SOLID principles
- Write self-documenting code with meaningful names
- Keep functions and methods small and focused on a single responsibility
- Apply consistent formatting and adhere to language-specific style guides
### 2. Language-Specific Practices
- **JavaScript/TypeScript**:
- Use strict typing in TypeScript
- Leverage modern ES6+ features appropriately
- Prefer functional programming patterns when appropriate
- **Python**:
- Follow PEP 8 style guide
- Use type hints for better code clarity
- Leverage virtual environments and dependency management
- **Go**:
- Follow Go's official style guide
- Embrace error handling patterns (no exceptions)
- Use interfaces for abstraction and testing
- **Java/Kotlin**:
- Utilize Spring best practices if applicable
- Follow standard naming conventions
- Use appropriate design patterns
### 3. Testing
- Implement thorough unit tests (aim for 80%+ coverage)
- Write integration tests for critical paths
- Use TDD/BDD where appropriate
- Implement end-to-end tests for critical user journeys
- Mock external dependencies appropriately
## Security Guidelines
### 1. Authentication & Authorization
- Implement OAuth 2.0 and OpenID Connect when appropriate
- Use JWT with proper expiration and signature validation
- Apply principle of least privilege
- Implement MFA for sensitive operations
### 2. Data Protection
- Encrypt sensitive data at rest and in transit
- Implement proper key management
- Follow GDPR, CCPA, and other relevant data protection regulations
- Have clear data retention and deletion policies
### 3. Code Security
- Scan for vulnerabilities in code and dependencies
- Follow OWASP Top 10 protections
- Implement CSP and other security headers
- Protect against common vulnerabilities (XSS, CSRF, SQL Injection)
## Performance & Scalability
### 1. Database Optimization
- Design schemas with performance in mind
- Use appropriate indexes
- Implement query optimization
- Consider read/write splitting for high-traffic applications
### 2. Caching Strategies
- Implement multi-level caching when appropriate
- Use Redis or similar for distributed caching
- Apply cache invalidation strategies
- Consider cache-aside, write-through, or write-behind patterns
### 3. Horizontal Scaling
- Design stateless services where possible
- Implement proper load balancing
- Use database sharding for large datasets
- Consider serverless architecture for appropriate workloads
## DevOps & CI/CD
### 1. Infrastructure as Code
- Use Terraform, CloudFormation, or similar tools
- Version control all infrastructure configurations
- Implement immutable infrastructure patterns
- Consider container orchestration with Kubernetes
### 2. CI/CD Pipeline
- Automate build, test, and deployment processes
- Implement feature flags for safe deployments
- Use blue/green or canary deployment strategies
- Incorporate security scanning in the pipeline
### 3. Monitoring & Observability
- Implement comprehensive logging
- Use distributed tracing for complex systems
- Set up proper metrics and alerting
- Follow SRE principles for reliability
## AI-Specific Guidelines
### 1. Model Development
- Document data sources and preprocessing steps
- Version control training data and model artifacts
- Validate models for bias and fairness
- Implement proper model monitoring
### 2. AI Ethics
- Ensure AI decisions are explainable when possible
- Implement human oversight for critical AI decisions
- Consider privacy implications of AI systems
- Test for and mitigate algorithmic bias
## Sustainability and Cost Optimization
### 1. Resource Efficiency
- Optimize resource utilization (CPU, memory, network)
- Implement auto-scaling based on demand
- Use appropriate instance types for the workload
- Consider serverless for appropriate use cases
### 2. Cost Management
- Implement tagging for resource attribution
- Set up cost alerting and budgeting
- Regularly review and optimize resource usage
- Consider spot instances for non-critical workloads
## Documentation
### 1. Code Documentation
- Document all public APIs
- Include context and rationale, not just what the code does
- Keep documentation close to the code
- Update documentation as code changes
### 2. Architectural Documentation
- Maintain high-level architecture diagrams
- Document system boundaries and integrations
- Capture design decisions and alternatives considered
- Use C4 model or similar for different detail levels
## Collaboration Patterns
### 1. Version Control
- Use feature branching or trunk-based development
- Write meaningful commit messages
- Implement proper code review process
- Consider monorepo vs. polyrepo approaches
### 2. Team Workflows
- Document coding standards for the team
- Establish clear definition of done
- Implement pair/mob programming for complex features
- Foster knowledge sharing and documentation
## Tech Stack Selection Criteria
### 1. Evaluation Factors
- Consider team expertise and learning curve
- Evaluate community support and ecosystem
- Assess long-term maintenance implications
- Balance innovation with stability
### 2. Technology Lifecycle
- Have a strategy for managing technical debt
- Plan for technology obsolescence
- Implement graceful deprecation strategies
- Regular assessments of current stack
---
This document should be reviewed and updated regularly to reflect emerging best practices and technologies. All team members should be familiar with these guidelines and apply them in their daily work with Cline AI assistance.


# Series of Prompts for Cline to Create Interview Prep Platform Boilerplate

Here's a series of prompts you can give to Cline in VSCode to create a complete boilerplate repository for the Interview Prep Platform:

## Prompt 1: Project Initialization and Architecture Design

```
Create a comprehensive project architecture for an Interview Prep Platform with the following components:

1. Next.js frontend with TypeScript
2. FastAPI backend with PostgreSQL
3. Authentication system
4. Payment integration with Stripe
5. AI feedback integration using OpenAI
6. Voice recording and transcription capabilities

Create the initial project structure with appropriate directories for both frontend and backend, following clean architecture principles. Include README.md with setup instructions and ai_guidelines.md in the root directory.
```

## Prompt 2: Frontend Development - Core Structure

```
Set up the Next.js frontend with the following:

1. Directory structure following the App Router pattern
2. Authentication context using NextAuth.js
3. Responsive layout with:
   - Header with navigation
   - Dashboard layout
   - Authentication pages (login/register)
4. Style setup with Tailwind CSS
5. Reusable UI components:
   - Button
   - Card
   - Modal
   - Form inputs
   - Timer component for interview sessions
6. State management with React Context or Redux Toolkit
7. Type definitions for all major data structures
```

## Prompt 3: Frontend Development - Features

```
Implement the following frontend feature components:

1. Question selection interface with filtering by category
2. Voice recording component with timer functionality
3. Playback and review interface for recorded answers
4. Self-assessment checklist component
5. Feedback display that shows AI-generated feedback
6. User profile and history section
7. Admin panel interface for:
   - Managing questions and categories
   - Creating assessment criteria
   - Viewing user statistics
   - Creating new product "clones"
8. Subscription management and payment interface
```

## Prompt 4: Backend API Development

```
Develop the FastAPI backend with the following endpoints and functionality:

1. User authentication API:
   - Registration, login, password reset
   - JWT token handling
   - User profile management

2. Question management API:
   - CRUD operations for questions and categories
   - Search and filtering capabilities
   - Admin-only access controls

3. Response handling API:
   - Saving user responses (audio files and transcriptions)
   - Processing assessment data
   - Generating and storing AI feedback

4. Subscription and payment API:
   - Integration with Stripe
   - Subscription status management
   - Payment webhook handling

5. Admin management API:
   - Platform clone creation
   - User management
   - Analytics endpoints

Include comprehensive error handling, validation, and security measures.
```

## Prompt 5: Database Schema and ORM Models

```
Design a PostgreSQL database schema with the following models:

1. User model:
   - Authentication details
   - Profile information
   - Subscription status

2. Question model:
   - Question content
   - Categories and tags
   - Assessment criteria

3. Response model:
   - Link to user and question
   - Audio file storage (or path)
   - Transcription text
   - Self-assessment data
   - AI feedback storage

4. Product/Platform model:
   - For managing multiple interview platforms

5. Subscription model:
   - Payment details
   - Subscription levels
   - Billing history

Create SQLAlchemy ORM models and migrations for all these entities with proper relationships and constraints.
```

## Prompt 6: AI Integration Services

```
Implement service integrations for AI and transcription capabilities:

1. Speech-to-text service:
   - Integration with Deepgram or similar API
   - Audio processing utilities
   - Error handling and retry logic

2. OpenAI feedback generation:
   - Service for generating personalized feedback
   - Prompt templates for different question types
   - Caching mechanism for similar responses

3. Create abstraction layers for these services to allow for:
   - Easy switching between providers
   - Local development without API costs
   - Comprehensive error handling
   - Rate limiting and quota management
```

## Prompt 7: Authentication and Authorization System

```
Implement a comprehensive authentication and authorization system:

1. User authentication:
   - JWT token handling
   - OAuth integration (Google, Facebook)
   - Email verification flows

2. Role-based access control:
   - User roles (user, admin, super-admin)
   - Permission management
   - Resource-level access controls

3. Security features:
   - Password hashing and security
   - Rate limiting for authentication attempts
   - CSRF protection
   - Secure cookie handling
```

## Prompt 8: Payment Integration

```
Set up Stripe integration for subscription management:

1. Subscription plans configuration
2. Payment processing workflow
3. Webhook handlers for subscription events
4. User subscription status management
5. Payment history and receipts
6. Handling subscription upgrades/downgrades
7. Trial period implementation
8. Failed payment handling
```

## Prompt 9: Testing Framework

```
Create a comprehensive testing framework for the application:

1. Unit tests:
   - Frontend component tests with React Testing Library
   - Backend service and utility tests

2. Integration tests:
   - API endpoint tests
   - Database interaction tests
   - Authentication flow tests

3. End-to-end tests:
   - Critical user journeys with Cypress or Playwright
   - Payment flow tests with Stripe test mode

4. Test utilities:
   - Test data generators
   - Mock services for external APIs
   - Authentication helpers for testing
```

## Prompt 10: DevOps and Deployment

```
Set up deployment configuration and CI/CD pipeline:

1. Docker configuration:
   - Dockerfile for frontend
   - Dockerfile for backend
   - Docker Compose for local development

2. GitHub Actions workflow for:
   - Running tests
   - Linting and code quality checks
   - Building and pushing Docker images
   - Deployment to staging/production

3. Environment configuration:
   - Environment variable management
   - Secret handling
   - Different configurations for dev/staging/production

4. Deployment instructions for:
   - Vercel (frontend)
   - Render or AWS (backend)
   - Database setup and migration
```

## Prompt 11: Documentation

```
Create comprehensive documentation for the project:

1. API documentation:
   - OpenAPI/Swagger docs for all endpoints
   - Usage examples

2. Developer documentation:
   - Setup instructions
   - Architecture overview
   - Contribution guidelines
   - Code style guide

3. User documentation:
   - Admin user guide
   - End-user guide
   - FAQ section

4. Database schema documentation:
   - ERD diagrams
   - Relationship explanations
   - Migration guidance
```

## Prompt 12: Security and Performance Optimization

```
Implement security measures and performance optimizations:

1. Security features:
   - Input validation
   - XSS protection
   - SQL injection prevention
   - Rate limiting
   - Security headers

2. Performance optimizations:
   - Database query optimization
   - Frontend bundle optimization
   - Image and asset optimization
   - API response caching
   - Lazy loading implementation
```

## Prompt 13: Monitoring and Analytics

```
Set up monitoring and analytics infrastructure:

1. Error tracking:
   - Integration with Sentry or similar service
   - Custom error boundaries
   - Structured logging

2. Performance monitoring:
   - API response time tracking
   - Database query performance
   - Frontend performance metrics

3. Usage analytics:
   - Basic analytics dashboard
   - User engagement metrics
   - Feature usage tracking
```

## Prompt 14: Accessibility and Internationalization

```
Implement accessibility features and internationalization:

1. Accessibility:
   - ARIA attributes
   - Keyboard navigation
   - Screen reader compatibility
   - Color contrast compliance

2. Internationalization:
   - i18n setup with next-intl or similar
   - Language selection UI
   - RTL language support
   - Date and number formatting
```

## Prompt 15: Final Review and Optimization

```
Perform a comprehensive review of the codebase:

1. Code quality:
   - Ensure consistent code style
   - Remove any redundant code
   - Optimize imports and dependencies

2. Documentation review:
   - Check all documentation for completeness
   - Ensure README is comprehensive

3. Performance audit:
   - Run Lighthouse audits on key pages
   - Optimize any performance bottlenecks

4. Security scan:
   - Run security audit on dependencies
   - Check for any security vulnerabilities

Package everything into a clean, well-documented template repository that can be easily cloned and customized.
```

These prompts will guide Cline through creating a comprehensive boilerplate for the Interview Prep Platform, following the guidelines in the ai_guidelines.md file. Each prompt builds on the previous ones, creating a complete and well-structured project that adheres to best practices.