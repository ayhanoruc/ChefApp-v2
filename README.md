# chef-app
this is the future of COOKING-COPILOT APPS

## TASK LIST:
--------------
-[X] clean the code, copy & save the source code in 2 places first, then do the changes.

-[X] clean-intended recipe format for all recipes that will be added from now on.

-[ ] solve exception handler bug: incorrect file_name.

-[ ] xlsx -> jsonDocumentGenerator -> VectorCreator-Adder pipeline. 
	- takes xlsx in corrext format, runs the pipeline, adds new recipes correctly.
	 or rejects the file, logs the error.


- [ ] adding GPT-3.5/4 into the loop:
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
-------------------
- MVP
- design:
    - canva:
        - login page:
            - credentials
        - register page:
            - credentials
            - country
            - allergics # to be improved
        - terms of service page
        - forget password page
        - inside the app:
            - my kitchen:
                - malzemeleri eklemek için bir tane box
                - ekledikçe aşagıda raf görünümlü ui ‘da güncellenecek
            - Cheff Master:
                - 5-6 preference yaptıracak açılır seçim listesi, bunlar recipe filtrelemesi için kullanılacak. zorunlu değil.
                - 10 stok cheff resmi
                - generate recipe butonu. tıklandıgında yükleme ekranı ve yeni recipe sayfası
            - Recipe sayfası:
                - defter görünümlü, ve sağ üst veya herhangi bir bölgede yemek resmi ve cheff resmi olacak.
                - yine bir köşede nutirtion info ve timingler olacak.
                - ingredients bilgisi listlenecek.
                - directions bilgisi listelenecek.
                - token token yazacak.
                - shopping list ui’ı eklenecek.
- frontend:
    - coding.
    - backend bağlantıları.
- Backend:
    - kullanıcı database’i, alergics
    - kullanıcı malzemeleri
    - processing→data ile iletişim, request-response
    - logging and exception handling
    
- ai + data:
    - database yeni recipe’ler ekleme.
    - user endpoint oluşturma. POST
    - preference, user language ve allergic’e göre filtreleme, + ingredients ‘a göre 1 yanıt çek.
    - gpt instruction prompt’u ayarla.
        - shopping list oluşturucu
        - dile göre translation.
    - databaseden dönen recipe’nin ingredient’ı uygun prompt ve user ingredient + dil ile gpt’ye yolla, en son formatı bu noktada alman gerek.
    - Json response olarak gönder