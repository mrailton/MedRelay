import '../css/app.css';
import Alpine from 'alpinejs';
import { subscribeRealtime } from './realtime.js';

window.Alpine = Alpine;
window.subscribeRealtime = subscribeRealtime;

Alpine.start();
