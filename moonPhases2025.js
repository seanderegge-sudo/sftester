/**
 * Returns the major lunar phases for the calendar year 2025.
 *
 * Each entry contains the UTC timestamp for the moment the phase occurs and a
 * human friendly label describing the phase.  The ephemeris values were
 * generated with the PyEphem (https://pypi.org/project/ephem/) astronomical
 * library using the VSOP87/ELP2000-82B models, then rounded to the nearest
 * second.
 *
 * @returns {Array<{phase: 'New Moon' | 'First Quarter' | 'Full Moon' | 'Last Quarter', date: string}>}
 */
export function listMoonPhases2025() {
  return [
    { phase: 'First Quarter', date: '2025-01-06T23:56:15Z' },
    { phase: 'Full Moon', date: '2025-01-13T22:26:51Z' },
    { phase: 'Last Quarter', date: '2025-01-21T20:30:45Z' },
    { phase: 'New Moon', date: '2025-01-29T12:35:55Z' },
    { phase: 'First Quarter', date: '2025-02-05T08:02:07Z' },
    { phase: 'Full Moon', date: '2025-02-12T13:53:20Z' },
    { phase: 'Last Quarter', date: '2025-02-20T17:32:30Z' },
    { phase: 'New Moon', date: '2025-02-28T00:44:46Z' },
    { phase: 'First Quarter', date: '2025-03-06T16:31:35Z' },
    { phase: 'Full Moon', date: '2025-03-14T06:54:35Z' },
    { phase: 'Last Quarter', date: '2025-03-22T11:29:23Z' },
    { phase: 'New Moon', date: '2025-03-29T10:57:47Z' },
    { phase: 'First Quarter', date: '2025-04-05T02:14:37Z' },
    { phase: 'Full Moon', date: '2025-04-13T00:22:12Z' },
    { phase: 'Last Quarter', date: '2025-04-21T01:35:29Z' },
    { phase: 'New Moon', date: '2025-04-27T19:31:06Z' },
    { phase: 'First Quarter', date: '2025-05-04T13:51:40Z' },
    { phase: 'Full Moon', date: '2025-05-12T16:55:53Z' },
    { phase: 'Last Quarter', date: '2025-05-20T11:58:41Z' },
    { phase: 'New Moon', date: '2025-05-27T03:02:17Z' },
    { phase: 'First Quarter', date: '2025-06-03T03:40:53Z' },
    { phase: 'Full Moon', date: '2025-06-11T07:43:46Z' },
    { phase: 'Last Quarter', date: '2025-06-18T19:19:02Z' },
    { phase: 'New Moon', date: '2025-06-25T10:31:32Z' },
    { phase: 'First Quarter', date: '2025-07-02T19:30:07Z' },
    { phase: 'Full Moon', date: '2025-07-10T20:36:42Z' },
    { phase: 'Last Quarter', date: '2025-07-18T00:37:36Z' },
    { phase: 'New Moon', date: '2025-07-24T19:11:07Z' },
    { phase: 'First Quarter', date: '2025-08-01T12:41:16Z' },
    { phase: 'Full Moon', date: '2025-08-09T07:54:59Z' },
    { phase: 'Last Quarter', date: '2025-08-16T05:12:10Z' },
    { phase: 'New Moon', date: '2025-08-23T06:06:28Z' },
    { phase: 'First Quarter', date: '2025-08-31T06:25:08Z' },
    { phase: 'Full Moon', date: '2025-09-07T18:08:49Z' },
    { phase: 'Last Quarter', date: '2025-09-14T10:32:53Z' },
    { phase: 'New Moon', date: '2025-09-21T19:54:04Z' },
    { phase: 'First Quarter', date: '2025-09-29T23:53:45Z' },
    { phase: 'Full Moon', date: '2025-10-07T03:47:33Z' },
    { phase: 'Last Quarter', date: '2025-10-13T18:12:37Z' },
    { phase: 'New Moon', date: '2025-10-21T12:25:08Z' },
    { phase: 'First Quarter', date: '2025-10-29T16:20:45Z' },
    { phase: 'Full Moon', date: '2025-11-05T13:19:15Z' },
    { phase: 'Last Quarter', date: '2025-11-12T05:28:04Z' },
    { phase: 'New Moon', date: '2025-11-20T06:47:13Z' },
    { phase: 'First Quarter', date: '2025-11-28T06:58:44Z' },
    { phase: 'Full Moon', date: '2025-12-04T23:14:01Z' },
    { phase: 'Last Quarter', date: '2025-12-11T20:51:38Z' },
    { phase: 'New Moon', date: '2025-12-20T01:43:17Z' },
    { phase: 'First Quarter', date: '2025-12-27T19:09:48Z' },
  ];
}
