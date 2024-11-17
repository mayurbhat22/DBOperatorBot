import { useEffect, useState, useRef } from "react";
import axios from "axios";
import "./App.css";
import ReactMarkdown from "react-markdown";
import gptLogo from "./assets/chatgpt.svg";
import addBtn from "./assets/add-30.png";
import home from "./assets/home.svg";
import sendBtn from "./assets/send.svg";
import userIcon from "./assets/user-icon.png";
import gptImgLogo from "./assets/chatgptLogo.svg";
import user from "./assets/user.png";
import logo from "./assets/QB.jpg";
function App() {
  const msgEnd = useRef(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      text: "Hello! I'm QueryBuddy. How can I assist you today?",
      isBot: true,
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { text: input, isBot: false }]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await axios.post(
        "https://queryaichat.azurewebsites.net/ask",
        JSON.stringify({
          question: input,
        })
      );

      setMessages((prev) => [
        ...prev,
        { text: response.data.answer, isBot: true },
      ]);
      setIsTyping(false);
    } catch (error) {
      console.error("Error communicating with backend:", error);
      setMessages((prev) => [
        ...prev,
        { text: "Error fetching response. Please try again.", isBot: true },
      ]);
    }
  };

  useEffect(() => {
    msgEnd.current.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleEnter = async (e) => {
    if (e.key === "Enter") {
      await handleSend();
    }
  };

  return (
    <>
      <div className="App">
        <div className="sideBar">
          <div className="upperSide">
            <div className="upperSideTop">
              <img src={logo} alt="" className="logo" />
              <span className="brand">QueryBuddy</span>
            </div>
            <button
              className="midBtn"
              onClick={() => {
                window.location.reload();
              }}
            >
              <img src={addBtn} alt="" className="addBtn" />
              NewChat
            </button>
          </div>
        </div>
        <div className="main">
          <div className="chats">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat ${msg.isBot ? "bot" : "user"}`}>
                <img className="chatImg" src={msg.isBot ? logo : user} alt="" />
                <p className="txt">
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </p>
              </div>
            ))}
            {isTyping && (
                <div className="message bot typing">
                    <span className="dot"></span>
                    <span className="dot"></span>
                    <span className="dot"></span>
                </div>
            )}
            <div ref={msgEnd} />
          </div>
          <div className="chatFooter">
            <div className="inp">
              <input
                type="text"
                placeholder="Send a Prompt"
                value={input}
                onKeyDown={handleEnter}
                onChange={(e) => {
                  setInput(e.target.value);
                }}
              />
              <button className="send" onClick={handleSend}>
                <img src={sendBtn} alt="" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
