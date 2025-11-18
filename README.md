# Tailspin Toys

This repository contains the project for a 1 hour guided workshop to explore GitHub Copilot Agent Mode and related features in Visual Studio Code. The project is a website for a fictional game crowd-funding company, with a [Flask](https://flask.palletsprojects.com/en/stable/) backend using [SQLAlchemy](https://www.sqlalchemy.org/) and [Astro](https://astro.build/) frontend using [Svelte](https://svelte.dev/) for dynamic pages.

📚 **[View Comprehensive Documentation](./DOCUMENTATION.md)** - For detailed information about the project, architecture, deployment, and development guidelines.

To begin the workshop, start at [docs/README.md](./docs/README.md)

Or, if just want to run the app...

## Launch the site

A script file has been created to launch the site. You can run it by:

```bash
./scripts/start-app.sh
```

Then navigate to the [website](http://localhost:4321) to see the site!

## Testing

This project includes comprehensive testing at multiple levels:

### Backend Tests
Unit tests for the Flask API endpoints:
```bash
./scripts/run-server-tests.sh
```

### Frontend E2E Tests  
Basic UI tests for the Astro/Svelte frontend:
```bash
cd client && npm run test:e2e
```

### Comprehensive End-to-End Tests
Full-stack integration tests that validate UI and API working together:

```bash
cd tests/e2e && npm install && npm test
```

These E2E tests:
- Validate API endpoints are working correctly and returning expected data
- Test UI components consume and display API data properly  
- Simulate complete user workflows (browsing games, viewing details, navigation)
- Ensure error handling works gracefully across the full stack
- Test performance and data consistency

The E2E tests automatically spin up both the Flask backend and Astro frontend servers, making them perfect for validating the complete application flow before deployment.

## License 

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) for the full terms.

## Maintainers 

You can find the list of maintainers in [CODEOWNERS](./.github/CODEOWNERS).

## Support

This project is provided as-is, and may be updated over time. If you have questions, please open an issue.
