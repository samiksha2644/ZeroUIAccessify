# Firestore Schema Documentation — PMPML Saarthi

## Collections

### `bus_stops`
Each document represents a single PMPML bus stop.

| Field      | Type              | Description                                     |
|------------|-------------------|-------------------------------------------------|
| `id`       | `string`          | Unique identifier (slug), e.g. `"swargate"`     |
| `name`     | `string`          | Human-readable name, e.g. `"Swargate"`          |
| `lat`      | `number (float)`  | Latitude of the stop                            |
| `lng`      | `number (float)`  | Longitude of the stop                           |
| `routes`   | `array<string>`   | List of `bus_routes` IDs that serve this stop    |

**Example document** (`bus_stops/swargate`):
```json
{
  "id": "swargate",
  "name": "Swargate",
  "lat": 18.5018,
  "lng": 73.8636,
  "routes": ["route_156", "route_11"]
}
```

---

### `bus_routes`
Each document represents a single bus route.

| Field               | Type              | Description                                        |
|---------------------|-------------------|----------------------------------------------------|
| `id`                | `string`          | Unique identifier, e.g. `"route_156"`              |
| `name`              | `string`          | Display name, e.g. `"Route 156"`                   |
| `stops`             | `array<string>`   | Ordered list of `bus_stops` IDs along the route     |
| `frequency_minutes` | `number (int)`    | Average interval between buses on this route        |

**Example document** (`bus_routes/route_156`):
```json
{
  "id": "route_156",
  "name": "Route 156",
  "stops": ["swargate", "deccan_gymkhana", "shivajinagar", "pune_station"],
  "frequency_minutes": 15
}
```

---

### `live_buses`
Each document represents a bus currently operating on a route.  
Updated by a real-time tracking system (simulated for MVP).

| Field               | Type              | Description                                       |
|---------------------|-------------------|---------------------------------------------------|
| `id`                | `string`          | Unique bus ID, e.g. `"bus_156_a"`                 |
| `route_id`          | `string`          | Reference to `bus_routes` document ID             |
| `current_stop_index`| `number (int)`    | Index into the route's `stops[]` array            |
| `last_updated`      | `string (ISO)`    | ISO-8601 timestamp of last position update        |

**Example document** (`live_buses/bus_156_a`):
```json
{
  "id": "bus_156_a",
  "route_id": "route_156",
  "current_stop_index": 1,
  "last_updated": "2026-04-11T07:00:00Z"
}
```

---

## Relationships Diagram

```
bus_stops.routes[]  ──────►  bus_routes.id
bus_routes.stops[]  ──────►  bus_stops.id
live_buses.route_id ──────►  bus_routes.id
```

## Indexes

For the MVP, no composite indexes are required beyond Firestore defaults.
If queries on `live_buses` are filtered by `route_id`, Firestore will auto-create
a single-field index on that property.
