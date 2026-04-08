import ChatSidebar from "./components/ChatSidebar";
import ChatArea from "./components/ChatArea";
import Visualization from "./components/Visualization";
import "./App.css";

function App() {
  return (
    <div className="app-layout">
      <aside className="app-sidebar">
        <ChatSidebar />
      </aside>
      <main className="app-main">
        <ChatArea />
      </main>
      <aside className="app-visualization">
        <Visualization />
      </aside>
    </div>
  );
}

export default App;
