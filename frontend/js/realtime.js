export function subscribeRealtime({ eventId, incidentId }) {
  const url = new URL('/realtime/events', window.location.origin);
  url.searchParams.set('event_id', eventId);
  if (incidentId) url.searchParams.set('incident_id', incidentId);
  const es = new EventSource(url);
  es.addEventListener('incident.updated', (e) => {
    const data = JSON.parse(e.data);
    if (!incidentId || data.incident?.id === incidentId) location.reload();
  });
  es.addEventListener('resource.updated', () => location.reload());
}
