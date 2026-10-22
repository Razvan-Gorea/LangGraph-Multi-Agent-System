"use client";

import { useEffect, useRef } from "react";
import type { Dispatch, FormEvent, KeyboardEvent, SetStateAction } from "react";
import { MdDelete } from "react-icons/md";

import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

export type Message = { id: string | number; body?: string | null };
export type Conversation = { id: string | number; title: string };

type ConversationHistoryProps = {
  conversation: boolean;
  conversationSideBarList: Conversation[];
  createConversationTitle: string;
  setCreateConversationTitle: Dispatch<SetStateAction<string>>;
  handleDelete: (id: Conversation["id"]) => void;
  swapConversations: (id: Conversation["id"]) => void;
  handleConversationEnter?: (e: KeyboardEvent<HTMLTextAreaElement>) => void;
};

export function ConversationHistory({
  conversation,
  conversationSideBarList,
  createConversationTitle,
  setCreateConversationTitle,
  handleDelete,
  swapConversations,
  handleConversationEnter,
}: ConversationHistoryProps) {
  return (
    <aside
      className={cn(
        "w-72 shrink-0 flex-col gap-3 border-r bg-sidebar p-4",
        conversation ? "flex" : "hidden",
      )}
    >
      <h3 className="text-sm font-semibold">Conversation History</h3>
      <form onSubmit={(e) => e.preventDefault()}>
        <Textarea
          required
          maxLength={20}
          rows={1}
          className="min-h-9 resize-none"
          placeholder="New Conversation"
          value={createConversationTitle}
          onChange={(e) => setCreateConversationTitle(e.target.value)}
          onKeyDown={handleConversationEnter}
        />
      </form>
      <ul className="flex flex-col gap-1 overflow-y-auto">
        {conversationSideBarList.map((item) => (
          <li
            key={item.id}
            className="flex items-center justify-between rounded-md hover:bg-accent"
          >
            <a
              href="#"
              className="flex-1 truncate px-3 py-2 text-sm"
              onClick={(e) => {
                e.preventDefault();
                swapConversations(item.id);
              }}
            >
              {item.title}
            </a>
            <button
              type="button"
              aria-label={`Delete ${item.title}`}
              className="mr-1 rounded p-2 text-muted-foreground hover:text-destructive"
              onClick={() => handleDelete(item.id)}
            >
              <MdDelete size={18} />
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}

// pending: the answer is being generated but no text has arrived yet
export function ChatDisplay({ chatLog, pending }: { chatLog: Message[]; pending?: boolean }) {
  const scrollableListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollableListRef.current;
    if (el && chatLog.length > 0) el.scrollTop = el.scrollHeight;
  }, [chatLog, pending]);

  return (
    <div ref={scrollableListRef} className="flex-1 overflow-y-auto p-4">
      <ul className="mx-auto flex max-w-3xl flex-col gap-3">
        {chatLog.map((item) => {
          const isBot = !!item.body && item.body.startsWith("Response:");
          return (
            <li
              key={item.id}
              data-role={isBot ? "bot" : "user"}
              className={cn(
                "max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2 text-sm",
                isBot
                  ? "self-start bg-muted"
                  : "self-end bg-primary text-primary-foreground",
              )}
            >
              {item.body
                ? isBot
                  ? item.body.replace(/^Response:\s*/, "")
                  : item.body
                : "Error: Content isn't available"}
            </li>
          );
        })}
        {pending && (
          <li className="self-start rounded-2xl bg-muted px-4 py-3">
            <span role="status" className="flex items-center gap-1">
              <span className="sr-only">Generating response</span>
              {[0, 150, 300].map((delay) => (
                <span
                  key={delay}
                  aria-hidden
                  className="size-1.5 animate-bounce rounded-full bg-muted-foreground/60"
                  style={{ animationDelay: `${delay}ms` }}
                />
              ))}
            </span>
          </li>
        )}
      </ul>
    </div>
  );
}

type ChatInputProps = {
  userQuery: string;
  setUserQuery: Dispatch<SetStateAction<string>>;
  handleSubmit: (e: FormEvent) => void;
  handleEnter: (e: KeyboardEvent<HTMLTextAreaElement>) => void;
};

export function ChatInput({
  userQuery,
  setUserQuery,
  handleSubmit,
  handleEnter,
}: ChatInputProps) {
  return (
    <form onSubmit={handleSubmit} className="mx-auto w-full max-w-3xl p-4">
      <Textarea
        rows={1}
        className="min-h-10 resize-none"
        value={userQuery}
        onChange={(e) => setUserQuery(e.target.value)}
        onKeyDown={handleEnter}
        placeholder="Enter your message"
      />
    </form>
  );
}
