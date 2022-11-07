import {useContext} from "react";
import {Link} from "react-router-dom";
import AuthContext from "../context/AuthContext";

const Navbar = () => {
    const {user, logoutUser} = useContext(AuthContext);
    return (
        <nav>
            <div>
                <h1>TicTacToe</h1>
                <div>
                    {user ? (
                        <ul>
                            <li><Link to="/">Home</Link></li>
                            <li><Link to="/play">Play</Link></li>
                            <li>
                                <button onClick={logoutUser}>Logout</button>
                            </li>
                        </ul>
                    ) : (
                        <ul>
                            <li><Link to="/login">Login</Link></li>
                            <li><Link to="/register">Register</Link></li>
                        </ul>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;