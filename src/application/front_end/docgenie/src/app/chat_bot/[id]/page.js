"use client";

import styles from "../../../../styles/Chat_Bot.module.css";
import { Rubik } from "next/font/google";
import { useEffect, useRef, useState } from "react";
import { RiChatHistoryLine } from "react-icons/ri";
import { MdDelete } from "react-icons/md";
import { useParams, useRouter } from "next/navigation";
import { GrSend } from "react-icons/gr";
import { CgProfile } from "react-icons/cg";
import { OrbitProgress } from "react-loading-indicators";

const rubik = Rubik({
    subsets: ["latin"],
    weight: ["300"],
}); 

export function ConversationHistory({
  conversation,
  conversationElement,
  conversationSideBarList,
  createConversationTitle,
  setCreateConversationTitle,
  createConversation,
  handleDelete,
  swapConversations,
  handleConversationEnter,
}) {
  return (
    <div ref={conversationElement} className={styles.conversation_history}>
      <h3 className={styles.title}>Conversation History</h3>
      <form>
        <textarea
          required
          maxLength={20}
          rows={1}
          className={styles.conversation_text_bar}
          type="text"
          placeholder="New Conversation"
          value={createConversationTitle}
          onChange={(e) => setCreateConversationTitle(e.target.value)}
          onKeyDown={handleConversationEnter}
          onFocus={(e) => e.target.placeholder = ""}
          onBlur={(e) => e.target.placeholder = "New Conversation"}
        />
        <button
          type="button"
          onClick={createConversation}
          className={styles.conversation_button}
        >
          +
        </button>
      </form>
      <div className={styles.scrollable_conversations_list}>
        <ul>
          {conversationSideBarList.map((item) => (
            <a
              key={item.id}
              href=""
              onClick={(e) => {
                e.preventDefault();
                swapConversations(item.id);
              }}
          >
              <li>
                <div className={styles.conversation_item}>
                  {item.title}
                  <div className={styles.delete_icon}>
                    <MdDelete
                      size={20}
                      onClick={() => handleDelete(item.id)}
                      type="button"
                      role="button"
                    />
                  </div>
                </div>
              </li>
            </a>
          ))}
        </ul>
      </div>
    </div>
  );
}

export function ChatDisplay(
{ 
    chatLog 
}) 
{
  const scrollableListRef = useRef(null);
    
  useEffect(() => {
      if (scrollableListRef.current && chatLog.length > 0) {
          const scrollableDiv = scrollableListRef.current;
          scrollableDiv.scrollTop = scrollableDiv.scrollHeight;
      }
  }, [chatLog]);
  
    return (
      
       <div ref={scrollableListRef} className={styles.scrollable_list}>
         <ul>
           {chatLog.map((item) => (
                
             <li key={item.id} 
             className={(item.body && item.body.startsWith("Response:")) ? styles.generated_message : styles.user_message}> 
             { item.body ? (
             item.body.startsWith("Response:") ? item.body.replace(/^Response:\s*/, '') : item.body 
             ) : "Error: Content isn't available"} 
             </li>
           ))}
         </ul>
       </div>
    );
}

export function ChatInput (
{
    isLoading,
    userQuery,
    setUserQuery,
    handleSubmit,
    handleEnter,
})
{
    return (
       <form onSubmit={handleSubmit}>
         <textarea
           rows={1}
           className={styles.text_bar}
           type="text"
           value={userQuery}
           onChange={(e) => setUserQuery(e.target.value)}
           onKeyDown={handleEnter}
           placeholder="Enter your message"
           onFocus={(e) => e.target.placeholder = ""}
           onBlur={(e) => e.target.placeholder = "Enter your message"}
           disabled={isLoading}
         />
         <button type="submit" className={styles.query_submit_button} disabled={isLoading}>
           <GrSend />
         </button>
       </form>
    );
}

export default function Chat_Bot() {
    const [userQuery, setUserQuery] = useState("");
    const [chatLog, setChatLog] = useState([]);
    const [conversation, setDisplayConversation] = useState(false);
    const [conversationSideBarList, setConversationSidebarList] = useState([]);
    const [createConversationTitle, setCreateConversationTitle] = useState("");
    const [currentConversation, setCurrentConversation] = useState("");
    const conversationElement = useRef(null);
    const [isLoading, setIsLoading] = useState(false);
    const params = useParams();
    const router = useRouter();

    useEffect(() => {
        if (currentConversation === ""){
            populateConversation();
        }

        if (conversationElement !== null){
            conversationElement.current.style.display = conversation ? "block": "none";
        }
    }, [conversation]);

    async function populateConversation(){
        const res = await fetch(
            `http://127.0.0.1:8888/conversation/latest?user_id=${params.id}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            }
        ); 
        const res_json = await res.json();
        setCurrentConversation(res_json.id);

        const chatRes = await fetch(
            `http://127.0.0.1:8888/conversation/${res_json.id}/chat/all`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            }
        );
        const chatRes_json = await chatRes.json();
        setChatLog(chatRes_json);

        const sideBarRes = await fetch(
            `http://127.0.0.1:8888/conversation/all?user_id=${params.id}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            }
        );
        const sideBarRes_json = await sideBarRes.json();
        setConversationSidebarList(sideBarRes_json);
    };

    const createConversation = async () => {
        if (createConversationTitle.trim()) {
            const convoRes = await fetch(
                `http://127.0.0.1:8888/conversation/create`, 
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        title: createConversationTitle,
                        user_id: params.id
                    }),
                }
            );
            const convoRes_json = await convoRes.json();
            setConversationSidebarList((prevConvos) => [...prevConvos, convoRes_json]);
            setCreateConversationTitle("");
        }
    };

    const handleConversationEnter = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            createConversation();
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setIsLoading(true);
        
        if (userQuery.trim()) {
          const res = await fetch(
              `http://127.0.0.1:8888/conversation/${currentConversation}/chat/create`,
              {
                  method: "POST",
                  headers: {
                      "Content-Type": "application/json",
                  },
                  body: JSON.stringify({
                      body: userQuery,
                      conversation_id: currentConversation,
                  }),
              }
          );
          const data = await res.json();
          setChatLog((prevLog) => [...prevLog, data]);
      }

        
        if (userQuery.trim()) {
            const res = await fetch(
                `http://127.0.0.1:8888/conversation/${currentConversation}/chat/response`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        body: userQuery,
                        conversation_id: currentConversation,
                    }),
                }
            );
            const data = await res.json();
            setChatLog((prevLog) => [...prevLog, data]);
            setUserQuery("");
            setIsLoading(false);
        }
    };

    const handleEnter = (e) => {
        if (e.key === "Enter" && !e.shiftKey){
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleDelete = async (id) => {
       const res = await fetch(
           `http://127.0.0.1:8888/conversation/${id}`,
            {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    id: id    
                }),
            }
       );
       if (res.ok) {
           populateConversation();
       }
    };

    const handleSettingsClick = () => {
      router.push(`/admin/${params.id}`);
    };

    const swapConversations = async (conversationID) => {
        setCurrentConversation(conversationID);

        const chatRes = await fetch(
            `http://127.0.0.1:8888/conversation/${conversationID}/chat/all`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                },
            }
        );
        if (chatRes.ok){
            const chatRes_json = await chatRes.json();
            setChatLog(chatRes_json);
        };
    };

    return (
        <main className={rubik.className}>
          <section className={styles.block}>
            <h2> DocGenie </h2>
          </section>
          <section className={styles.section_zone}>
            <div className={styles.settings_icon}>
              <CgProfile size={40} onClick={handleSettingsClick}/>
              <span className={styles.settings_message}> Admin </span>
            </div>
          </section>
          <section>
            <div className={styles.icon}>
              <RiChatHistoryLine
                size={40}
                onClick={() => {
                  if (conversation){
                    setDisplayConversation(false);
                  }
                  else {
                    setDisplayConversation(true)
                  }
                }}
              />
              <span className={styles.message}> Show/Hide Conversation History </span>
            </div>
          </section>
          <section>
            <ConversationHistory
              conversation={conversation}
              conversationElement={conversationElement}
              conversationSideBarList={conversationSideBarList}
              createConversationTitle={createConversationTitle}
              setCreateConversationTitle={setCreateConversationTitle}
              createConversation={createConversation}
              handleDelete={handleDelete}
              swapConversations={swapConversations}
              handleConversationEnter={handleConversationEnter}
            />
          </section>
          <section>
            <ChatDisplay chatLog={chatLog} />
          </section>
          <section>
            <ChatInput 
              userQuery={userQuery}
              setUserQuery={setUserQuery}
              handleSubmit={handleSubmit}
              handleEnter={handleEnter}
              isLoading={isLoading}
            />
          </section>
          <section>
            <div className={styles.loading_indicator}>
              {isLoading && <OrbitProgress variant="dotted" color="#0070f3" size="small" text="" textColor="" />}
            </div>
          </section>
        </main>
    );
}