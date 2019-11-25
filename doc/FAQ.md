## Debug

Common problems:

1. When starting RP I get an error:
```
InnerError={"code":"ForbiddenByPolicy"} 
```

Solution: Check if your env is set with up-to-date credentials, and if your keyvault has Access Policy for the right `aad-team-shared` and `engineering` account as per `deploy.json` file.