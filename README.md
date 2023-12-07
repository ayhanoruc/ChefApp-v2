# chef-app
this is the future of COOKING-COPILOT APPS

## TASK LIST:
--------------
-[ ] clean the code, copy & save the source code in 2 places first, then do the changes.

-[ ] clean-intended recipe format for all recipes that will be added from now on.

-[ ] xlsx -> jsonDocumentGenerator -> VectorCreator-Adder pipeline. 
	- takes xlsx in corrext format, runs the pipeline, adds new recipes correctly.
	 or rejects the file, logs the error.

- [ ] adding GPT-3.5/4 to the loop:
	- the recipe json will be passed to GPT3.5
	- gpt3.5 will check the relevance of the recipe regarding the user ingredients.
	- gpt will calculate the missing ingredients and generate a shopping list.
	- handle gpt errors, add try-again logic. If 3 trial ends with error, just provide 
	  the raw recipe json to the user.

- [ ] improve async behaviour by : threading, asyncio etc.

- [ ] after all pipelines working correctly, deploy to digitalocean droplet:
	- test various resources
	- conduct api load test, mimic user behaviour.


---------------------
- Start Docker engine
- `docker build -t chefapp-fastapi .`
- `docker run -p 8000:8000 chefapp-fastapi` 
- push the image to DockerHub

Digital Ocean Server
----
- create ssh private-public keys: `ssh-keygen -t rsa`
- enter passphrase if needed
- check the public key: 
    [`cd %USERPROFILE%\.ssh`] then [`type id_rsa.pub`]
- copy this public key, and create droplet using this ssh as credential instead of username-password
- after initializing the droplet you can connect to the server by: `ssh root@ip_adress`
