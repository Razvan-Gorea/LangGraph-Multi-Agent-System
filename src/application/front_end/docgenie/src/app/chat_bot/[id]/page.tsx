"use client";

import { useEffect, useState } from "react";
import type { FormEvent, KeyboardEvent } from "react";
import { RiChatHistoryLine } from "react-icons/ri";
import { useParams, useRouter } from "next/navigation";
import { CgProfile } from "react-icons/cg";

import {
  ChatDisplay,
  ChatInput,
  ConversationHistory,
  type Conversation,
  type Message,
} from "@/components/chat";

const API = "http://127.0.0.1:8888";
const JSON_HEADERS = { "Content-Type": "application/json" };

export default function Chat_Bot() {
  const [userQuery, setUserQuery] = useState("");
  const [chatLog, setChatLog] = useState<Message[]>([]);
  const [conversation, setDisplayConversation] = useState(false);
  const [conversationSideBarList, setConversationSidebarList] = useState<Conversation[]>([]);
  const [createConversationTitle, setCreateConversationTitle] = useState("");
  const [currentConversation, setCurrentConversation] = useState<string | number>("");
  const [isLoading, setIsLoading] = useState(false);
  const params = useParams<{ id: string }>();
  const router = useRouter();

  useEffect(() => {
    populateConversation();
  }, []);

  async function populateConversation() {
    const res = await fetch(`${API}/conversation/latest?user_id=${params.id}`, {
      method: "POST",
      headers: JSON_HEADERS,
    });
    const res_json = await res.json();
    setCurrentConversation(res_json.id);

    const chatRes = await fetch(`${API}/conversation/${res_json.id}/chat/all`, {
      method: "GET",
      headers: JSON_HEADERS,
    });
    setChatLog(await chatRes.json());

    const sideBarRes = await fetch(`${API}/conversation/all?user_id=${params.id}`, {
      method: "POST",
      headers: JSON_HEADERS,
    });
    setConversationSidebarList(await sideBarRes.json());
  }

  const createConversation = async () => {
    if (createConversationTitle.trim()) {
      const convoRes = await fetch(`${API}/conversation/create`, {
        method: "POST",
        headers: JSON_HEADERS,
        body: JSON.stringify({ title: createConversationTitle, user_id: params.id }),
      });
      const convoRes_json = await convoRes.json();
      setConversationSidebarList((prevConvos) => [...prevConvos, convoRes_json]);
      setCreateConversationTitle("");
    }
  };

  const handleConversationEnter = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      createConversation();
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!userQuery.trim() || isLoading) return;

    setIsLoading(true);
    const body = JSON.stringify({ body: userQuery, conversation_id: currentConversation });
    setUserQuery("");

    const res = await fetch(`${API}/conversation/${currentConversation}/chat/create`, {
      method: "POST",
      headers: JSON_HEADERS,
      body,
    });
    const data = await res.json();
    setChatLog((prevLog) => [...prevLog, data]);

    try {
      const response = await fetch(`${API}/conversation/${currentConversation}/chat/response/stream`, {
        method: "POST",
        headers: JSON_HEADERS,
        body,
      });
      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      // the "Response:" prefix is what ChatDisplay uses to tell bot messages from user ones
      const id = `stream-${Date.now()}`;
      let text = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        text += decoder.decode(value, { stream: true });
        const reply = { id, body: "Response:" + text };
        setChatLog((prevLog) =>
          prevLog.some((m) => m.id === id)
            ? prevLog.map((m) => (m.id === id ? reply : m))
            : [...prevLog, reply],
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleEnter = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleDelete = async (id: Conversation["id"]) => {
    const res = await fetch(`${API}/conversation/${id}`, {
      method: "DELETE",
      headers: JSON_HEADERS,
      body: JSON.stringify({ id }),
    });
    if (res.ok) {
      populateConversation();
    }
  };

  const handleSettingsClick = () => {
    router.push(`/admin/${params.id}`);
  };

  const swapConversations = async (conversationID: Conversation["id"]) => {
    setCurrentConversation(conversationID);

    const chatRes = await fetch(`${API}/conversation/${conversationID}/chat/all`, {
      method: "GET",
      headers: JSON_HEADERS,
    });
    if (chatRes.ok) {
      setChatLog(await chatRes.json());
    }
  };

  return (
    <main className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="rounded-md p-2 hover:bg-accent"
            onClick={() => setDisplayConversation((open) => !open)}
          >
            <RiChatHistoryLine size={24} />
            <span className="sr-only">Show/Hide Conversation History</span>
          </button>
          <h2 className="text-lg font-semibold"> DocGenie </h2>
        </div>
        <button
          type="button"
          className="flex items-center gap-2 rounded-md p-2 hover:bg-accent"
          onClick={handleSettingsClick}
        >
          <CgProfile size={24} />
          <span className="text-sm"> Admin </span>
        </button>
      </header>
      <div className="flex min-h-0 flex-1">
        <ConversationHistory
          conversation={conversation}
          conversationSideBarList={conversationSideBarList}
          createConversationTitle={createConversationTitle}
          setCreateConversationTitle={setCreateConversationTitle}
          handleDelete={handleDelete}
          swapConversations={swapConversations}
          handleConversationEnter={handleConversationEnter}
        />
        <section className="flex min-w-0 flex-1 flex-col">
          {/* dots show until the first streamed token creates the bot message */}
          <ChatDisplay
            chatLog={chatLog}
            pending={isLoading && !chatLog.at(-1)?.body?.startsWith("Response:")}
          />
          <ChatInput
            userQuery={userQuery}
            setUserQuery={setUserQuery}
            handleSubmit={handleSubmit}
            handleEnter={handleEnter}
          />
        </section>
      </div>
    </main>
  );
}
