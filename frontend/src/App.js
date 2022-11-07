import React from "react";
import "./index.css";
import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import { BrowserRouter, Route, Switch } from "react-router-dom";
import PrivateRoute from "./utils/PrivateRoute";
import { AuthProvider } from "./context/AuthContext";
import Home from "./views/homePage";
import Login from "./views/loginPage";
import Register from "./views/registerPage";
import PlayPage from "./views/playPage";

function App() {
  return (
      <BrowserRouter forceRefresh={true}>
        <div>
          <AuthProvider>
            <Navbar />
            <Switch>
              <Route component={Login} path="/login" />
              <Route component={Register} path="/register" />
              <PrivateRoute component={PlayPage} path="/play" />
              <Route component={Home} path="/" />
            </Switch>
          </AuthProvider>
          <Footer />
        </div>
      </BrowserRouter>
  );
}

export default App;