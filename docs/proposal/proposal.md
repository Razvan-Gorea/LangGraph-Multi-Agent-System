# School of Computing &mdash; Year 4 Project Proposal Form

## SECTION A

|                     |                   |
|---------------------|-------------------|
|Project Title:       | DocGenie          |
|Student 1 Name:      | Shane Power       |
|Student 1 ID:        | 21308533          |
|Student 2 Name:      | Razvan Gorea      |
|Student 2 ID:        | 21306373          |
|Project Supervisor:  | Tomas Ward        |

## SECTION B

### Introduction

The general area covered by this project is web development, large language models, multi-agents, vector databases and information retrival.

### Outline

This project aims to take some collection of disconnected SQL databases, along with various document stores, and centralise them within one vector database. With this database, we can now perform Retrieval Augmented Generation, on this database, and serve a response back to a user, who requested some information.  

For example, some user might want to know about some data which is stored across multiple datastores, in multiple formats. This user input is vectorised, compared against our vectorised database, which is a combination of our underlying datastores, and our system returns some context, which is given with the prompt to a LLM to generate a response. This response is then served back to the user, through some user interface.

We aim to retain both strict access control and retain good scalability, as we increase the data being covered under this system. Access control is vital, as are the privacy issues raised by unifying all of these data stores.  

In addition, the large number of data stores involved poses problems for scalability. One single RAG agent will struggle to work with large amounts of data.  

As such, a multi-agent approach is needed. By specialising different agents within the system to perform individual functions, you can ensure scalability while minimising the chance of hallucination.

### Background

The idea largely stemmed from both of our INTRA experiences.

One one hand, the overall project idea originated in Razvans INTRA project. This project provided the initial problem of having some fragmented data stores, and needing some centralised point of query.  
In that instance, there was not enough time to fully explore and implement the idea. Only a few weeks were given to design, architect and develop the system, so the fourth year project became a good opportunity to develop a more complete version of that original idea, while also increasing the complexity.

In contrast, during Shanes INTRA placement, he was not working with a Retrieval Augmented System at all, but was instead working more with manual indexing of multiple SQL servers, and sharing data across them. This is of course a prime use case of RAG, and so he became interested in how to scale the process of indexing and search across large fragmented databases, while maintaining a "plug and play" mentality towards adding additional databases to the system.

### Achievements

The users will be both technical and non-technical employees of private businesses and organisations. The project will provide a customized information retrieval service to businesses and organisations in the form of a user friendly chatbot interface on the web.

The non-technical users can be served by this RAG system, but technical users who have no need for RAG but require the centralisation of the underlying fragmented databases can bypass RAG, and query these different databases in one place, Thus allowing for flexiblity. 


### Justification

This project is most useful in a business with multiple fragmented databases, that have a need to be queried together and where access control must be enforced.

This project is also useful where there is a need for a highly scalable solution, i.e. where traditional Retrieval Augmented Generation is not viable due to large datasets being too much for a single agent to handle.

As such, large businesses would get the most usage out of this system.

### Programming language(s)

The backend would be written in Python, while the frontend would be written in JavaScript.

### Programming tools / Tech stack

For the database component, MongoDB would be used to store both the SQL data and the document stores, as it can vectorise documents.
This simplifies the process of being able to query both stores.

LangChain will be used to build our stateful, multi-actor system which can handle the RAG and access control element of the project. LangChain would also handle an orchestration layer, where we could co-ordinate our agents.

NextJS would be used to build the frontend chatbot. 
### Hardware

No non-standard hardware is required.

### Learning Challenges

The main challenges can be sub-divided into some more sections.

#### Evaluation
Evaluating a RAG systme is quite difficult, and so you need to have some set evaluation plan, as without one it will be impossible to judge if context guarding is been followed. We plan to have a diverse amount of datastores, with some pre-built conflicts between them. This will allow us to use these special contexts as tests in our retrieval agent. If this context is returned, given some pre-defined prompt, we know that the system is not functioning. This would form the backbone of our testing suite.
We will use deepeval to evaluate the retrieval agent.

#### Technologies
The main technology of concern here would be LangChain. This framework is used to write stateful multi-actor applications, and both of us have no real experience in using this library.
While this library is new, it offers a huge depth of features, due to its large support base. This introduces the issue of maintainability.  

When choosing what multi-agent framework to use, our primary concern was the speed and age of these frameworks.  
Multi-Agent RAG is a very new field, and so frameworks built to support it might only be a year old.  

This means these frameworks are prone to change, and often have unfinished design. This means that we need to be very careful about relying on the framework in its current state.

MongoDB is also a new technology to both of us. While we are both familiar with SQL, the process of reconciling the data between the document stores and SQL data into some vector database will require some thought and trial-and-error.

The frontend chatbot would be written in NextJS, as it provides Server Side Rendering (SSR).

#### Experience
An additional challenge posed is through our experience with the topics of Large-Language Models and Retrieval Augmented Generation. Neither of us had any real experience in designing these types of systems, but both of us had experienced challenges that these systems solve, or had used pre-build systems using these topics, such as Azure Search Service. As such, our lack of experience can pose a challenge.

### Breakdown of work

#### Shane
Database set up (Seeding) (CSV)  
Database set up (Seeding) (JSON)  
Database set up (Seeding) (BSON)  
Writing the special agent for reading  
Writing the special agent for retrieving  
Integration testing  
Writing the general LangChain framework  

#### Razvan
Frontend client  
Reconciling the databases  
Vectorising the databases  
End-To-End testing  
Writing the agent for database reconciliation  
Writing the special agent for orchestration  
