import {useEffect, useState} from "react";
import useAxios from "../utils/useAxios";

function Statistics() {
    const [rows, setRows] = useState({});
    const api = useAxios();


    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get("/statistics/");
                setRows(response.data['statistics']);

            } catch {
                setRows({error: ['', '', '']})
            }
        };
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <div>
            <p>Statistics</p>
            <div>
                <div>
                    <table>
                        <thead>
                        <tr>
                            <th>Username</th>
                            <th>Wins</th>
                            <th>Draws</th>
                            <th>Loses</th>
                        </tr>
                        </thead>
                        <tbody>
                        {Object.keys(rows).map((key) => (
                            <tr>
                                <td>{key}</td>
                                <td>{rows[key][0]}</td>
                                <td>{rows[key][1]}</td>
                                <td>{rows[key][2]}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default Statistics;