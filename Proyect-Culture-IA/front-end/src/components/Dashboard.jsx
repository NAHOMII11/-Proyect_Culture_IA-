import React, { useEffect, useState } from "react";
import { API } from "../config/api";
import { httpClient } from "../utils/httpClient";

const Dashboard = () => {
  const [places, setPlaces] = useState([]);
  const [ranking, setRanking] = useState([]);
  const [generatedRoutes, setGeneratedRoutes] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);

        const [placesRes, rankingRes, routesRes] = await Promise.all([
          httpClient.get(API.bff.dashplaces),
          httpClient.get(API.bff.ranking),
          httpClient.get(API.bff.routes).catch(() => ({ data: { data: [] } })),
        ]);

        const placesPayload = placesRes.data?.featured_products ?? placesRes.data;
        const placesData = Array.isArray(placesPayload) ? placesPayload : [];

        const rankingPayload = rankingRes.data?.data ?? rankingRes.data;
        const rankingData = Array.isArray(rankingPayload) ? rankingPayload : [];

        const routesPayload = routesRes.data?.data ?? routesRes.data;
        const routesList = Array.isArray(routesPayload) ? routesPayload : [];

        setPlaces(placesData);
        setRanking(rankingData);
        setGeneratedRoutes(routesList.length);

        setError("");
      } catch (err) {
        console.error(err);
        setError(
          "No se pudieron cargar los indicadores"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();

    const interval = setInterval(
      fetchDashboard,
      30000
    );

    return () => clearInterval(interval);
  }, []);

  if (loading)
    return <div>Cargando dashboard...</div>;

  if (error)
    return (
      <div style={{ color: "red", padding: 20 }}>
        {error}
      </div>
    );

  // ============================
  // KPIs reales
  // ============================

  const totalPlaces = places.length;

  const geolocatedPlaces = places.filter(
    (p) => p.latitude && p.longitude
  ).length;
const averageScore =
  ranking.length > 0
    ? `${(
        (ranking.reduce(
          (acc, item) =>
            acc + Number(item.score || 0),
          0
        ) /
          ranking.length) *
        100
      ).toFixed(2)}%`
    : "0%";

  const topPlace =
    ranking[0]?.name ||
    "Sin registros";

  return (
    <div
      style={{
        padding: "30px",
      }}
    >
      <h1>Dashboard Cultural</h1>
      <p>
        Indicadores clave del sistema
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit,minmax(250px,1fr))",
          gap: "20px",
          marginTop: "30px",
        }}
      >
        <div className="kpi-card">
          <h3>Total de lugares</h3>
          <p>{totalPlaces}</p>
        </div>

        <div className="kpi-card">
          <h3>Lugares geolocalizados</h3>
          <p>{geolocatedPlaces}</p>
        </div>

        <div className="kpi-card">
          <h3>Score promedio</h3>
          <p>{averageScore}</p>
        </div>

        <div className="kpi-card">
          <h3>Lugar más visitado</h3>
          <p>{topPlace}</p>
        </div>

        <div className="kpi-card">
          <h3>Rutas generadas</h3>
          <p>{generatedRoutes}</p>
        </div>
      </div>

      <div style={{ marginTop: 40 }}>
        <h2>Top 5 lugares</h2>

        {ranking.length === 0 ? (
          <p>No hay ranking disponible</p>
        ) : (
          <ul>
            {ranking
              .slice(0, 5)
              .map((item, index) => (
                <li
                  key={item.place_id}
                  style={{
                    marginBottom: 12,
                    fontSize: "16px",
                  }}
                >
                  #{index + 1}{" "}
                  <strong>
                    {item.name}
                  </strong>{" "}
                  — Score:{" "}
                 {(Number(item.score) * 100).toFixed(2)}%
                </li>
              ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Dashboard;