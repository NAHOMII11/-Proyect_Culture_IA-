import React, { useEffect, useState } from "react";

function App() {

  const [places, setPlaces] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/analytics/ranking")
      .then((res) => res.json())
      .then((data) => {
        console.log("DATOS DEL BACKEND:", data);
        setPlaces(data);
      })
      .catch((error) => console.error("Error:", error));
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>🏆 Ranking de Lugares</h1>

      <table
        style={{
          width: "80%",
          margin: "20 auto",
          textAlign: "center",
          borderCollapse: "collapse",
          borderRadius: "10px",
          overflow: "hidden",
          boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
          backgroundColor: "#fff",
        }}
      >
        <thead style={{ background: "#ebf3ea", color: "black" }}>
          <tr>
            <th style={{ padding: "12px" }}>#</th>
            <th style={{ padding: "12px" }}>Nombre</th>
            <th style={{ padding: "12px" }}>Ciudad</th>
            <th style={{ padding: "12px" }}>Score</th>
          </tr>
        </thead>

        <tbody>
          {places.map((place, index) => (
            <tr
              key={index}
              style={{
                backgroundColor:
                  index === 0
                    ? "#f7f7f7"
                    : index === 1
                    ? "#f7f7f7"
                    : index === 2
                    ? "#f7f7f7"
                    : index % 2 === 0
                    ? "#ffffff"
                    : "#fafafa",
              }}
            >
              <td style={{ padding: "10px", borderBottom: "1px solid #eee" }}>
                {index + 1}
              </td>
              <td style={{ padding: "10px", borderBottom: "1px solid #eee" }}>
                {place.name}
              </td>
              <td style={{ padding: "10px", borderBottom: "1px solid #eee" }}>
                {place.city}
              </td>
              <td style={{ padding: "10px", borderBottom: "1px solid #eee" }}>
                {place.score}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

    </div>
  );
}

export default App;