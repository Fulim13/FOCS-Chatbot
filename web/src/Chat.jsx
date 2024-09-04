import "./App.css";
import { useState, useEffect } from "react";
import "./index.css";
import "bootstrap/dist/css/bootstrap.css";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";

import {
  ChatContainer,
  MessageList,
  Message,
  Avatar,
  TypingIndicator,
  Button,
} from "@chatscope/chat-ui-kit-react";

import Form from "react-bootstrap/Form";
import InputGroup from "react-bootstrap/InputGroup";

function Chat() {
  const [data, setData] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [firstResponse, setFirstResponse] = useState(true);

  useEffect(() => {
    // Fetch initial data or previous messages if needed
  }, []);

  const handleSendMessage = (message) => {
    // Add the outgoing message to the data immediately
    const outgoingMessage = {
      direction: "outgoing",
      message:
        typeof message === "string"
          ? message
          : typeof inputMessage === "string"
          ? inputMessage
          : JSON.stringify(inputMessage),
      position: "single",
      sender: "You",
      sentTime: new Date().toLocaleTimeString(),
    };

    setData([...data, outgoingMessage]);
    setInputMessage(""); // Clear the input field right away
    setIsLoading(true);

    // Proceed to send the message to the backend
    fetch("http://localhost:8000/test/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: outgoingMessage.message,
      }),
    })
      .then((res) => res.json())
      .then((response) => {
        // Add the incoming response to the data
        const incomingMessage = {
          direction: "incoming",
          message: response.data,
          position: "single",
          sender: "Assistant",
          sentTime: new Date().toLocaleTimeString(),
        };
        setData((prevData) => [...prevData, incomingMessage]);
        setFirstResponse(false);
        setIsLoading(false);
      });
  };

  return (
    <div>
      <div>
        <header>
          <p>Chat Interface</p>
        </header>
        <ChatContainer
          style={{
            height: "500px",
            width: "800px",
          }}
        >
          <MessageList
            typingIndicator={
              isLoading ? (
                <TypingIndicator content="Response is generating" />
              ) : null
            }
          >
            {firstResponse && (
              <div className="flex">
                <Button
                  onClick={() => {
                    handleSendMessage(
                      "What is the Fee of Degree in Software Engineering"
                    );
                  }}
                >
                  What is the Fee of Degree in Software Engineering
                </Button>
                <Button
                  onClick={() => {
                    handleSendMessage("What programme I can enroll in Sabah");
                  }}
                >
                  What programme I can enroll in Sabah
                </Button>
                <Button
                  onClick={() => {
                    handleSendMessage(
                      "When is the intake of Degree in Software Engineering"
                    );
                  }}
                >
                  When is the intake of Degree in Software Engineering
                </Button>
              </div>
            )}
            {data.map((msg, index) => (
              <Message
                key={index}
                model={{
                  direction: msg.direction,
                  message: msg.message,
                  position: msg.position,
                  sender: msg.sender,
                  sentTime: msg.sentTime,
                }}
                className={msg.direction === "incoming" ? "text-left" : ""}
              >
                {msg.direction === "incoming" && (
                  <Avatar
                    name={msg.sender}
                    src="https://chatscope.io/storybook/react/assets/emily-xzL8sDL2.svg"
                  />
                )}
              </Message>
            ))}
          </MessageList>
        </ChatContainer>
        <InputGroup className="mb-3">
          <Form.Control
            placeholder="Type your message here"
            aria-label="Message"
            aria-describedby="button-addon2"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
          />
          <Button
            variant="outline-secondary"
            id="button-addon2"
            onClick={handleSendMessage}
          >
            Send
          </Button>
        </InputGroup>
      </div>
    </div>
  );
}

export default Chat;
