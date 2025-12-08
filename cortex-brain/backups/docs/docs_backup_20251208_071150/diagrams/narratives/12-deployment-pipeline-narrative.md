# CORTEX Deployment Pipeline

This diagram shows CORTEX's release process across environments.

**Dev** environment is where features are developed and unit tested.

**Staging** environment mirrors production for integration testing and validation.

**Production** environment is the live release where users interact with CORTEX.

Each environment transition requires passing automated tests - no manual "it worked on my machine" deployments. This pipeline ensures reliability and consistency across releases.

CORTEX uses git-based workflows - commits trigger CI/CD pipelines that validate, test, and deploy automatically.