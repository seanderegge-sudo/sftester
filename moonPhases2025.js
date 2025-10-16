/**
 * Tabulated major lunar phases for the calendar year 2025.
 *
 * The ephemeris timestamps were generated with the PyEphem astronomical
 * library (VSOP87/ELP2000-82B) and then rounded to the nearest second.  Each
 * entry is exported as an immutable record so consumers always receive
 * consistent data without worrying about accidental mutation.
 *
 * @typedef {'New Moon' | 'First Quarter' | 'Full Moon' | 'Last Quarter'} MoonPhaseName
 * @typedef {Object} MoonPhaseEntry
 * @property {MoonPhaseName} phase Human-friendly name of the lunar phase.
 * @property {string} iso ISO-8601 UTC timestamp for the phase occurrence.
 * @property {Date} date JavaScript Date representing the same instant as the ISO string.
 * @property {number} timestamp Milliseconds since the Unix epoch for quick comparisons.
 */

/**
 * Immutable catalogue of 2025 lunar phases keyed by occurrence.
 * @type {readonly MoonPhaseEntry[]}
 */
const MOON_PHASES_2025 = Object.freeze(
  [
    ['First Quarter', '2025-01-06T23:56:15Z'],
    ['Full Moon', '2025-01-13T22:26:51Z'],
    ['Last Quarter', '2025-01-21T20:30:45Z'],
    ['New Moon', '2025-01-29T12:35:55Z'],
    ['First Quarter', '2025-02-05T08:02:07Z'],
    ['Full Moon', '2025-02-12T13:53:20Z'],
    ['Last Quarter', '2025-02-20T17:32:30Z'],
    ['New Moon', '2025-02-28T00:44:46Z'],
    ['First Quarter', '2025-03-06T16:31:35Z'],
    ['Full Moon', '2025-03-14T06:54:35Z'],
    ['Last Quarter', '2025-03-22T11:29:23Z'],
    ['New Moon', '2025-03-29T10:57:47Z'],
    ['First Quarter', '2025-04-05T02:14:37Z'],
    ['Full Moon', '2025-04-13T00:22:12Z'],
    ['Last Quarter', '2025-04-21T01:35:29Z'],
    ['New Moon', '2025-04-27T19:31:06Z'],
    ['First Quarter', '2025-05-04T13:51:40Z'],
    ['Full Moon', '2025-05-12T16:55:53Z'],
    ['Last Quarter', '2025-05-20T11:58:41Z'],
    ['New Moon', '2025-05-27T03:02:17Z'],
    ['First Quarter', '2025-06-03T03:40:53Z'],
    ['Full Moon', '2025-06-11T07:43:46Z'],
    ['Last Quarter', '2025-06-18T19:19:02Z'],
    ['New Moon', '2025-06-25T10:31:32Z'],
    ['First Quarter', '2025-07-02T19:30:07Z'],
    ['Full Moon', '2025-07-10T20:36:42Z'],
    ['Last Quarter', '2025-07-18T00:37:36Z'],
    ['New Moon', '2025-07-24T19:11:07Z'],
    ['First Quarter', '2025-08-01T12:41:16Z'],
    ['Full Moon', '2025-08-09T07:54:59Z'],
    ['Last Quarter', '2025-08-16T05:12:10Z'],
    ['New Moon', '2025-08-23T06:06:28Z'],
    ['First Quarter', '2025-08-31T06:25:08Z'],
    ['Full Moon', '2025-09-07T18:08:49Z'],
    ['Last Quarter', '2025-09-14T10:32:53Z'],
    ['New Moon', '2025-09-21T19:54:04Z'],
    ['First Quarter', '2025-09-29T23:53:45Z'],
    ['Full Moon', '2025-10-07T03:47:33Z'],
    ['Last Quarter', '2025-10-13T18:12:37Z'],
    ['New Moon', '2025-10-21T12:25:08Z'],
    ['First Quarter', '2025-10-29T16:20:45Z'],
    ['Full Moon', '2025-11-05T13:19:15Z'],
    ['Last Quarter', '2025-11-12T05:28:04Z'],
    ['New Moon', '2025-11-20T06:47:13Z'],
    ['First Quarter', '2025-11-28T06:58:44Z'],
    ['Full Moon', '2025-12-04T23:14:01Z'],
    ['Last Quarter', '2025-12-11T20:51:38Z'],
    ['New Moon', '2025-12-20T01:43:17Z'],
    ['First Quarter', '2025-12-27T19:09:48Z'],
  ].map(([phase, iso]) =>
    Object.freeze({
      phase,
      iso,
      date: new Date(iso),
      timestamp: Date.parse(iso),
    }),
  ),
);

/**
 * Returns a deep copy of the immutable moon phase catalogue.
 *
 * @returns {MoonPhaseEntry[]}
 */
export function listMoonPhases2025() {
  return MOON_PHASES_2025.map((entry) => ({ ...entry, date: new Date(entry.date.getTime()) }));
}

/**
 * Formats the 2025 lunar phases into human-readable strings.
 *
 * @param {Intl.DateTimeFormatOptions & { locale?: string }} [options]
 *   Optional locale-aware formatting overrides passed to Intl.DateTimeFormat.
 * @returns {string[]} Human-readable strings (e.g. "2025-01-06 – First Quarter – 11:56 PM UTC").
 */
export function formatMoonPhases2025(options = {}) {
  const { locale = 'en-US', ...formatOptions } = options;
  const formatter = new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short',
    ...formatOptions,
  });

  return MOON_PHASES_2025.map((entry) => {
    const dateParts = formatter.format(entry.date);
    return `${dateParts} – ${entry.phase}`;
  });
}

export { MOON_PHASES_2025 };
