import "bootstrap/dist/css/bootstrap.min.css";
import { Routes, Route } from "react-router-dom";
import { Link } from "react-router-dom";
import Container from "react-bootstrap/Container";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import NavDropdown from "react-bootstrap/NavDropdown";
import Chat from "./Chat";

const Home = () => <h2>Home Page</h2>;
const ProgrammeFC = () => <h2>Programme Foundation in Computing Page</h2>;
const ProgrammeDCS = () => <h2>Programme Diploma in Computer Science Page</h2>;
const ProgrammeDIT = () => (
  <h2>Programme Diploma in Information Technology Page</h2>
);
const ProgrammeBSE = () => (
  <h2>Programme Bachelor Degree in Software Engineering Page</h2>
);
const ProgrammeBDS = () => (
  <h2>Programme Bachelor Degree in Data Science Page</h2>
);

const Navigation = () => {
  return (
    <Navbar expand="lg" className="bg-body-tertiary">
      <Container>
        <Navbar.Brand href="/">FOCS</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link>
              <Link to="/">Home</Link>
            </Nav.Link>
            <NavDropdown title="Programmes" id="basic-nav-dropdown">
              <NavDropdown.Item>
                <Link to="/programme/foundation-computing">
                  Foundation in Computing
                </Link>
              </NavDropdown.Item>
              <NavDropdown.Item>
                <Link to="/programme/diploma-cs">
                  Diploma in Computer Science
                </Link>
              </NavDropdown.Item>
              <NavDropdown.Item>
                <Link to="/programme/diploma-it">Diploma in IT</Link>
              </NavDropdown.Item>
              <NavDropdown.Item>
                <Link to="/programme/degree-se">
                  Bachelor Degree in Software Engineering
                </Link>
              </NavDropdown.Item>
              <NavDropdown.Item>
                <Link to="/programme/degree-ds">
                  Bachelor Degree in Data Science
                </Link>
              </NavDropdown.Item>
            </NavDropdown>
            <Nav.Link>
              <Link to="/chat">Chat</Link>
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

const App = () => {
  return (
    <div>
      <Navigation />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route
          path="/programme/foundation-computing"
          element={<ProgrammeFC />}
        />
        <Route path="/programme/diploma-cs" element={<ProgrammeDCS />} />
        <Route path="/programme/diploma-it" element={<ProgrammeDIT />} />
        <Route path="/programme/degree-se" element={<ProgrammeBSE />} />
        <Route path="/programme/degree-ds" element={<ProgrammeBDS />} />
        <Route path="/chat" element={<Chat />} />
      </Routes>
    </div>
  );
};

export default App;
