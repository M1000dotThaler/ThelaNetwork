
# THELA - Layer 1 Crypto

🤝Thela is a Cryptocurrency maded by yhe  community for the community, a small supply is  made that will be distributed among the contributors in this project.                                   

😑 We don't want Centralization, we don't want CEOs or companies behind us, we don't want ETFs... 

😀Feel free to make a Pull Request for this project with the improvements you think of.  
And if you are not a Dev, you can contribute with the graphics section.

> [!NOTE]  
> The project is not done... So you can collab, feel free :)

## Deployment

To deploy this project run

a)
```cmd
  git clone https://github.com/M1000dotThaler/ThelaNetwork.git
```

b)
```cmd
 pip install -r requirements.txt
```
c)
```cmd
python ThelaCore.py
```


## Sintaxsis to make a transaction 

```json
{
    "sender" : "",
    "receiver" : "",
    "amount" : ""
}

```

After this, open a APIs platform to make requests to the API of the Thela_Network.py maded in Flask.
## Features

- /Mine_Block
- /Get_Chain
- /is_valid
- /add_transaction
- /add_node(manually)
- /replace_chain(manually)
- /generate_wallet
- /check_balance/<adress>

>[!IMPORTANT]  
>Currently there is an error when adding a transaction to the blockchain, due to errors in signing the transaction with the private key of the address. (Feel free to try to fix it 🙂 )

 
## Contributing

Contributions are always welcome!





Fork the Repository:
       
       Click on the "Fork" button in the top-right corner of the page. This will create a copy of the repository in your GitHub account.

Clone Your Forked Repository:

```cmd
  git clone https://github.com/your-username/repository-name.git
```


Navigate into the cloned repository directory:


    cd repository-name

Create a New Branch:
```cmd
  git checkout -b my-new-feature
```

Make Changes:

    Make the necessary changes to the source code

Stage and Commit Your Changes:

```cmd
  git add .
```

This command stages all changes. If you want to stage specific files, replace . with the file names.


Commit your changes using the git commit command:

```cmd
  git commit -m "Specific Description of the changes"
```


Push Changes to Your Forked Repository:

```cmd
  git push origin name-of-your-branch
```


Create a Pull Request (PR):

    Go to your forked repository on GitHub.
    You should see a message indicating that you've recently pushed a new branch. Click on the "Compare & pull request" button next to it.
     Click on "Create pull request".

Wait for Review:

    The maintainers of the original repository will review your pull request. 

Syncing Your Forked Repository (Optional):

    If changes have been made to the original repository after you forked it, you may want to sync your fork with the original repository. You can do this using the following commands:

        git remote add upstream https://github.com/original-owner/repository-name.git
        git fetch upstream
        git checkout main
        git merge upstream/main
        git push origin main

        This will update your forked repository with any changes made to the original repository.

That's it! You've contributed to the ThelaNetwork! 

Thanks u very much :)

## Roadmap

Phase 1:

- Fix errors in the add_transaction call(error in trying to sign with the private key of the 
public adress the transaction)
 - Objective : Make secure and be sure that the only who can make a transaction of a public adress is
   the user that have the private_key

- Make a max supply of 1000000 Thelas

- Improve the conectivity and sync of the network with the rest of the nodes

Phase 2:

- Create a UI & desktop .exe that make the conectivity with the network and mining option 

- Simple wallet with out starting a node

- Block explorer

Phase 3:

-Create a Web 

-Marketing(logo...)

Be continued...



## License

[MIT](https://choosealicense.com/licenses/mit/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.