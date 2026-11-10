import React, { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Send,
  Trash2,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import type { LanguageCode } from "../i18n/translations";
import { translations } from "../i18n/translations";
import { streamChat } from "../api/sse";
import { api, ApiError } from "../api/client";
import type { SourceResponse } from "../types";
import { SafeAnswerRenderer } from "../components/SafeAnswerRenderer";
import { SourcePanel } from "../components/SourcePanel";
import { EmergencyCard } from "../components/EmergencyCard";

interface ChatProps {
  language: LanguageCode;
  onLanguageChange: (lang: LanguageCode) => void;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  emergency?: boolean;
  citations?: number[];
  sources?: SourceResponse[];
  feedbackSent?: "up" | "down";
}

interface SpeechRecognitionEvent {
  results: {
    [key: number]: {
      [key: number]: {
        transcript: string;
      };
    };
  };
}

interface SpeechRecognitionInstance {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
}

export const Chat: React.FC<ChatProps> = ({ language, onLanguageChange: _onLanguageChange }) => {
  const [searchParams] = useSearchParams();
  const t = translations[language] || translations.en;

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState(() => searchParams.get("q") || "");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Citation Source Panel state
  const [selectedCitation, setSelectedCitation] = useState<number | null>(null);
  const [activeSources, setActiveSources] = useState<SourceResponse[]>([]);

  // Speech Recognition & Synthesis states
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);

  // Session ID persistence
  const [sessionId] = useState<string>(() => {
    let sid = localStorage.getItem("swasthya_session_id");
    if (!sid) {
      sid = "sess_" + Math.random().toString(36).substring(2, 12);
      localStorage.setItem("swasthya_session_id", sid);
    }
    return sid;
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const stopSpeaking = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const sendMessage = async (messageText?: string) => {
    const textToSend = (messageText || input).trim();
    if (!textToSend || isLoading) return;

    setInput("");
    setErrorMessage(null);
    stopSpeaking();

    const userMsgId = `msg_${messages.length + 1}_user`;
    const assistantMsgId = `msg_${messages.length + 1}_ast`;

    const newUserMessage: ChatMessage = {
      id: userMsgId,
      role: "user",
      content: textToSend,
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    // Initial assistant placeholder
    setMessages((prev) => [
      ...prev,
      {
        id: assistantMsgId,
        role: "assistant",
        content: "",
        citations: [],
        sources: [],
      },
    ]);

    let accumulatedAnswer = "";
    let capturedSources: SourceResponse[] = [];
    let isEmergency = false;

    await streamChat(
      {
        message: textToSend,
        session_id: sessionId,
        language,
      },
      {
        onChunk: (chunk: string) => {
          accumulatedAnswer += chunk;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsgId ? { ...m, content: accumulatedAnswer } : m
            )
          );
        },
        onMetadata: (metadata) => {
          capturedSources = metadata.sources || [];
          isEmergency = metadata.emergency || false;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsgId
                ? {
                    ...m,
                    sources: capturedSources,
                    emergency: isEmergency,
                  }
                : m
            )
          );
        },
        onError: (err) => {
          console.error("Streaming error:", err);
          setIsLoading(false);
          if (err instanceof ApiError && err.status === 429) {
            setErrorMessage(t.errorRateLimit);
          } else {
            setErrorMessage(t.errorGeneric);
          }
        },
        onDone: () => {
          setIsLoading(false);
        },
      }
    );
  };

  // Auto scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Speech Recognition Setup
  useEffect(() => {
    const win = window as unknown as {
      SpeechRecognition?: new () => SpeechRecognitionInstance;
      webkitSpeechRecognition?: new () => SpeechRecognitionInstance;
    };
    const SpeechRecognition = win.SpeechRecognition || win.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = language === "hi" ? "hi-IN" : language === "pa" ? "pa-IN" : "en-IN";
      rec.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsListening(false);
      };
      rec.onerror = () => setIsListening(false);
      rec.onend = () => setIsListening(false);
      recognitionRef.current = rec;
    }
  }, [language]);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert("Voice input is not supported by your browser.");
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setIsListening(true);
      recognitionRef.current.lang = language === "hi" ? "hi-IN" : "en-IN";
      recognitionRef.current.start();
    }
  };

  // Text to Speech
  const speakText = (text: string) => {
    if (!window.speechSynthesis) return;
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }
    const cleanText = text.replace(/\[\d+(?:,\s*\d+)*\]/g, "");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = language === "hi" ? "hi-IN" : "en-IN";
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const handleCitationClick = (citationNumber: number, sources: SourceResponse[]) => {
    setActiveSources(sources);
    setSelectedCitation(citationNumber);
  };

  const handleFeedback = async (msgId: string, rating: "up" | "down") => {
    try {
      await api.postFeedback({
        session_id: sessionId,
        rating,
        comment: null,
      });
      setMessages((prev) =>
        prev.map((m) => (m.id === msgId ? { ...m, feedbackSent: rating } : m))
      );
    } catch (e) {
      console.error("Feedback error:", e);
    }
  };

  const clearChat = () => {
    stopSpeaking();
    setMessages([]);
    setSelectedCitation(null);
    setErrorMessage(null);
  };

  const quickPrompts = [
    { text: "What are malaria symptoms?", text_hi: "मलेरिया के लक्षण क्या हैं?" },
    { text: "How is tuberculosis treated?", text_hi: "टीबी का इलाज कैसे होता है?" },
    { text: "Vaccines due at 9 months", text_hi: "9 महीने के बच्चे के टीके" },
    { text: "Dengue warning signs", text_hi: "डेंगू के गंभीर लक्षण" },
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-5xl mx-auto px-2 sm:px-4 py-2 relative">
      {/* Top action bar: Clear chat + Language selector */}
      <div className="flex items-center justify-between pb-2 border-b border-zinc-200 dark:border-zinc-800">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/80 px-2.5 py-1 rounded-md border border-emerald-200 dark:border-emerald-800">
            Awareness Chat (Grounded RAG)
          </span>
        </div>
        <div className="flex items-center gap-2">
          {messages.length > 0 && (
            <button
              type="button"
              onClick={clearChat}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-zinc-600 dark:text-zinc-300 hover:text-red-600 dark:hover:text-red-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg transition focus:outline-none focus:ring-2 focus:ring-emerald-500"
              aria-label="Clear chat messages"
            >
              <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
              <span>{t.clear}</span>
            </button>
          )}
        </div>
      </div>

      {/* Persistent Visible Emergency Notice */}
      <div
        data-testid="persistent-emergency-notice"
        className="mt-2 mb-1 px-3 py-1.5 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 rounded-lg flex items-center justify-between text-xs text-red-800 dark:text-red-300"
        role="note"
      >
        <div className="flex items-center gap-1.5 font-medium">
          <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400 shrink-0" aria-hidden="true" />
          <span>
            {language === "hi"
              ? "आपातकाल में तुरंत 108 या 112 पर कॉल करें या नजदीकी अस्पताल जाएँ।"
              : language === "or"
              ? "ଜରୁରୀକାଳୀନ ପରିସ୍ଥିତିରେ ତୁରନ୍ତ ୧୦୮ ବା ୧୧୨ କୁ କଲ୍ କରନ୍ତୁ କିମ୍ବା ନିକଟତମ ଡାକ୍ତରଖାନାକୁ ଯାଆନ୍ତୁ।"
              : "In a medical emergency, immediately call 108 or 112 or visit the nearest hospital."}
          </span>
        </div>
        <div className="flex items-center gap-2 shrink-0 ml-2">
          <a
            href="tel:108"
            className="font-bold underline hover:text-red-950 dark:hover:text-red-200"
          >
            {language === "hi" ? "कॉल 108" : language === "or" ? "କଲ୍ ୧୦୮" : "Call 108"}
          </a>
          <span className="text-red-400 dark:text-red-600">|</span>
          <a
            href="tel:112"
            className="font-bold underline hover:text-red-950 dark:hover:text-red-200"
          >
            {language === "hi" ? "कॉल 112" : language === "or" ? "କଲ୍ ୧୧୨" : "Call 112"}
          </a>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-6">
            <div className="p-4 bg-emerald-100 dark:bg-emerald-950/70 text-emerald-600 dark:text-emerald-400 rounded-2xl">
              <Sparkles className="w-8 h-8" aria-hidden="true" />
            </div>
            <div className="max-w-md space-y-2">
              <h2 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">{t.appName}</h2>
              <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                {t.tagline}. Ask any awareness question in English or Hindi below.
              </p>
            </div>

            {/* Quick chips */}
            <div className="w-full max-w-lg space-y-2 pt-2">
              <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                {t.quickQuestionsTitle}
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                {quickPrompts.map((q, idx) => {
                  const label = language === "hi" ? q.text_hi : q.text;
                  return (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => sendMessage(label)}
                      className="px-3 py-1.5 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 hover:border-emerald-500 rounded-full text-xs font-medium text-zinc-700 dark:text-zinc-300 shadow-sm transition hover:bg-zinc-50 dark:hover:bg-zinc-750 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    >
                      {label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
            >
              {msg.role === "user" ? (
                <div className="max-w-[85%] sm:max-w-[75%] px-4 py-3 bg-emerald-600 text-white rounded-2xl rounded-tr-sm shadow-sm text-base leading-relaxed break-words">
                  {msg.content}
                </div>
              ) : (
                <div className="max-w-full sm:max-w-[90%] bg-white dark:bg-zinc-800/90 border border-zinc-200 dark:border-zinc-700/80 rounded-2xl rounded-tl-sm p-5 shadow-sm space-y-4">
                  {/* Emergency Warning Banner if detected */}
                  {msg.emergency && (
                    <EmergencyCard message={msg.content} callLabel={t.emergencyCallNow} />
                  )}

                  {/* Render content with safe interactive citation chips */}
                  {!msg.emergency && (
                    <SafeAnswerRenderer
                      text={msg.content}
                      onCitationClick={(n) => handleCitationClick(n, msg.sources || [])}
                      selectedCitation={selectedCitation}
                    />
                  )}

                  {/* Action row: Audio Read Aloud & Thumbs up/down feedback */}
                  {msg.content && !isLoading && (
                    <div className="flex items-center justify-between pt-3 border-t border-zinc-100 dark:border-zinc-700/60 text-xs text-zinc-500">
                      <div className="flex items-center gap-1">
                        <button
                          type="button"
                          onClick={() => speakText(msg.content)}
                          className="inline-flex items-center gap-1 p-1.5 hover:bg-zinc-100 dark:hover:bg-zinc-700 rounded-md transition focus:outline-none focus:ring-2 focus:ring-emerald-500"
                          title={isSpeaking ? t.stopAudioTooltip : t.readAloudTooltip}
                          aria-label={isSpeaking ? t.stopAudioTooltip : t.readAloudTooltip}
                        >
                          {isSpeaking ? (
                            <VolumeX className="w-4 h-4 text-red-500" aria-hidden="true" />
                          ) : (
                            <Volume2 className="w-4 h-4 text-zinc-500" aria-hidden="true" />
                          )}
                          <span className="hidden sm:inline">
                            {isSpeaking ? "Stop" : "Read Aloud"}
                          </span>
                        </button>
                      </div>

                      {/* Helpful Feedback */}
                      <div className="flex items-center gap-1">
                        <span className="mr-1">{t.feedbackHelpful}?</span>
                        <button
                          type="button"
                          onClick={() => handleFeedback(msg.id, "up")}
                          className={`p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition ${
                            msg.feedbackSent === "up" ? "text-emerald-600 bg-emerald-50 dark:bg-emerald-950/80 font-bold" : ""
                          }`}
                          title="Mark answer helpful"
                          aria-label="Mark helpful"
                        >
                          <ThumbsUp className="w-3.5 h-3.5" aria-hidden="true" />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleFeedback(msg.id, "down")}
                          className={`p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition ${
                            msg.feedbackSent === "down" ? "text-red-600 bg-red-50 dark:bg-red-950/80 font-bold" : ""
                          }`}
                          title="Mark answer unhelpful"
                          aria-label="Mark unhelpful"
                        >
                          <ThumbsDown className="w-3.5 h-3.5" aria-hidden="true" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-center gap-2 p-4 text-sm text-zinc-500 dark:text-zinc-400 bg-white dark:bg-zinc-800 rounded-2xl border border-zinc-200 dark:border-zinc-700 max-w-xs animate-pulse">
            <RefreshCw className="w-4 h-4 animate-spin text-emerald-600" aria-hidden="true" />
            <span>Consulting official health manuals...</span>
          </div>
        )}

        {/* Error notification */}
        {errorMessage && (
          <div role="alert" className="p-4 bg-red-50 dark:bg-red-950/80 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 text-sm flex items-start gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" aria-hidden="true" />
            <div className="space-y-1">
              <p className="font-semibold">{errorMessage}</p>
              <button
                type="button"
                onClick={() => sendMessage(messages[messages.length - 1]?.content)}
                className="text-xs font-bold underline hover:no-underline"
              >
                Retry last query
              </button>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage();
        }}
        className="pt-2 border-t border-zinc-200 dark:border-zinc-800 space-y-2"
      >
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? t.listening : t.chatPlaceholder}
            disabled={isLoading}
            className="w-full pl-4 pr-24 py-3.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-xl text-base text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-sm disabled:opacity-50"
            aria-label="Public health question input"
          />

          <div className="absolute right-2 flex items-center gap-1.5">
            {/* Mic Button */}
            <button
              type="button"
              onClick={toggleListening}
              className={`p-2 rounded-lg transition focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                isListening
                  ? "bg-red-600 text-white animate-pulse"
                  : "text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-700"
              }`}
              title={t.speakTooltip}
              aria-label={t.speakTooltip}
            >
              {isListening ? <MicOff className="w-5 h-5" aria-hidden="true" /> : <Mic className="w-5 h-5" aria-hidden="true" />}
            </button>

            {/* Send Button */}
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="p-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white rounded-lg shadow-sm transition focus:outline-none focus:ring-2 focus:ring-emerald-500"
              title={t.send}
              aria-label={t.send}
            >
              <Send className="w-5 h-5" aria-hidden="true" />
            </button>
          </div>
        </div>

        {/* Persistent bottom disclaimer */}
        <p className="text-[11px] text-center text-zinc-500 dark:text-zinc-400">
          {t.disclaimer}
        </p>
      </form>

      {/* Cited Source Document Side Drawer */}
      <SourcePanel
        sources={activeSources}
        selectedNumber={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />
    </div>
  );
};
