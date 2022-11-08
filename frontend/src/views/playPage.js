import {useEffect, useState} from "react";
import useAxios from "../utils/useAxios";

const TEN_SECONDS_IN_MS = 10000

const CellStyle = {
    height: '100px', width: '100px', border: '1px solid black', textAlign: 'center', userSelect: 'none'
}

/*game_info = {
    'game_state': game_state,
    'is_player_move': is_player_move,
    'is_x_move': is_x_move,
    'is_game_finished': is_game_finished,
    'last_move_date': last_move_date,
    'result': result,
    'is_player_winner': is_player_winner
}*/

/*find_game_info = {
    'is_player_in_queue': is_player_in_queue,
    'is_player_in_game': is_player_in_game,
    'description': description
}*/

function PlayPage() {
    const [res, setRes] = useState("");
    const [queueInfo, setQueueInfo] = useState("")
    const [isGameActive, setIsGameActive] = useState(false)
    const [gameState, setGameState] = useState("_________")
    const [isPlayerMove, setIsPlayerMove] = useState(false)
    const [isXMove, setIsXMove] = useState(true)
    const [lastMoveDate, setLastMoveDate] = useState("")
    const [result, setResult] = useState(null)
    const [isPlayerWinner, setIsPlayerWinner] = useState(null)
    const [isGameFinished, setIsGameFinished] = useState(null)
    const api = useAxios();

    const updateStatesFromGameInfo = async (json_data) => {
        setGameState(json_data['game_state'])
        setIsPlayerMove(json_data['is_player_move'])
        setIsXMove(json_data['is_x_move'])
        setLastMoveDate(json_data['last_move_date'])
        setResult(json_data['result'])
        setIsPlayerWinner(json_data['is_player_winner'])
        setIsGameFinished(json_data['is_game_finished'])
        console.log()
        console.log(isGameFinished)
    }

    const decideOnCurrentGame = async () => {

    }

    const currentGame = async () => {
        try {
            const response = await api.get("/current_game/")
            await updateStatesFromGameInfo(response.data)
            if (!response.data['is_game_finished']) {
                setIsGameActive(true)
                if (!response.data['is_player_move']) {
                    setTimeout(() => {
                        currentGame();
                    }, TEN_SECONDS_IN_MS)
                }
            }

        } catch {
            setRes("Something went wrong");
        }
    }

    const makeMove = async (field_number) => {
        if (isPlayerMove && gameState[field_number] === "_") {
            try {
                const response = await api.post("/make_move/", {'move_index': field_number})
                if (response.status === 200) {
                    if (response.data['is_game_finished'] === true) {
                        await updateStatesFromGameInfo(response.data)
                    } else {
                        setTimeout(() => {
                            currentGame();
                        }, TEN_SECONDS_IN_MS)
                    }
                }
            } catch {
            }
        }
    }

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.post("/find_game/");
                setRes(response.data.response);
                setQueueInfo(response.data['description'])
                if (response.data['is_player_in_queue']) {
                    setTimeout(() => {
                        fetchData();
                    }, TEN_SECONDS_IN_MS)
                } else if (response.data['is_player_in_game']) {
                    await currentGame()
                }
            } catch {
                setRes("Something went wrong");
            }
        };
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (<div>
        {isGameFinished || isGameActive ? <p>Good luck</p> : <p>{queueInfo}</p>}
        <div style={{display: isGameActive ? 'block' : 'none'}}>
            {isGameFinished ? <div>{isPlayerWinner ? 'You won' : (result === 0) ? 'Draw' : 'You lost'}</div> :
                <div>Currently moving: {isXMove ? 'x' : 'o'} ({isPlayerMove ? 'You' : 'Opponent'})</div>}
            <div>
                <table>
                    <tbody>
                    <tr>
                        <td style={CellStyle} onClick={() => makeMove(0)}>{gameState[0]}</td>
                        <td style={CellStyle} onClick={() => makeMove(1)}>{gameState[1]}</td>
                        <td style={CellStyle} onClick={() => makeMove(2)}>{gameState[2]}</td>
                    </tr>
                    <tr>
                        <td style={CellStyle} onClick={() => makeMove(3)}>{gameState[3]}</td>
                        <td style={CellStyle} onClick={() => makeMove(4)}>{gameState[4]}</td>
                        <td style={CellStyle} onClick={() => makeMove(5)}>{gameState[5]}</td>
                    </tr>
                    <tr>
                        <td style={CellStyle} onClick={() => makeMove(6)}>{gameState[6]}</td>
                        <td style={CellStyle} onClick={() => makeMove(7)}>{gameState[7]}</td>
                        <td style={CellStyle} onClick={() => makeMove(8)}>{gameState[8]}</td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>);
}

export default PlayPage;