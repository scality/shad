# SHAD

<p align="center">
  <img src="Figures/Overview.png" width="700"/>
</p>

**SHAD** (Scality High-dimensional Anomaly Detection benchmark) is a benchmark built from 
Scality RING distributed storage platform. SHAD includes both normal and anomalous series, with curated anomalies affecting different architectural layers. 
The dataset comprises 144 high-dimensional time series with per-dimension labels and detailed documentation describing anomaly type, affected components, and severity. 
The XML annotations also contains a detailed documentation of each of the 171 dimensions characterizing the series, enabling explicit mapping of each sensor to system components and roles. 
## License
The source code and datasets associated with this research project are released under the AGPL-3.0-only license.
By using, modifying, or redistributing this material, you agree to comply with the terms of the license.

# Repository Overview

`Dataset/` contains all labeled time series, grouped by experiment type, indexed by experiment id.

`Annotations/` contains all XML annotations, indexed by the experiment id they correspond to. 

## List of experiments
In what follows we provide the list of experiments per anomaly type.

### Nominal 

- 1773251393, ran on quarry7 starting at 2026-03-11 17:49
- 1773251399, ran on quarry8 starting at 2026-03-11 17:49
- 1773343560, ran on quarry starting at 2026-03-12 19:26
- 1773343565, ran on quarry2 starting at 2026-03-12 19:26
- 1773343568, ran on quarry3 starting at 2026-03-12 19:26
- 1773521107, ran on quarry starting at 2026-03-14 20:45
- 1773521116, ran on quarry2 starting at 2026-03-14 20:45
- 1773521128, ran on quarry3 starting at 2026-03-14 20:45
- 1773521135, ran on quarry4 starting at 2026-03-14 20:45
- 1773521150, ran on quarry5 starting at 2026-03-14 20:45
- 1773521156, ran on quarry7 starting at 2026-03-14 20:45
- 1773680909, ran on quarry 8 starting at 2026-03-16 17:08

### Single Disk Failure
- 1773343796, ran on quarry4 starting at 2026-03-12 19:29, with a failure on store 1 g2disk01 at time 3h30m for 1h30m
- 1773343802, ran on quarry5 starting at 2026-03-12 19:30, with a failure on store 3 g2disk02 at time 6h for 35m 
- 1773343833, ran on quarry6 starting at 2026-03-12 19:30, with a failure on store 3 g1disk02 at time 7h15m for 2h30m 
- 1773343804, ran on quarry7 starting at 2026-03-12 19:30, with a failure on store 1 g2disk01 at time 10h for 10m 
- 1773343837, ran on quarry8 starting at 2026-03-12 19:30, with a failure on store 1 g2disk02 at time 8h45m for 3h15m 
- 1773603342, ran on quarry starting at 2026-03-15 19:35, with a failure on store 2 g2disk01 at time 9h30m for 20m 
- 1773603348, ran on quarry2 starting at 2026-03-15 19:35, with a failure on store 1 g1disk01 at time 10h15m for 4h 
- 1773603351, ran on quarry3 starting at 2026-03-15 19:35, with a failure on store 1 g2disk01 at time 11h for 50m 
- 1773603363, ran on quarry4 starting at 2026-03-15 19:36, with a failure on store 2 g2disk01 at time 12h30m for 1h10m 
- 1773603383, ran on quarry5 starting at 2026-03-15 19:36, with a failure on store 3 g1disk02 at time 14h30m for 2h

### Simultaneous Disk Failure

- 1773429303, ran on quarry starting at2026-03-13 19:15, with 2 simultaneous disk failures on store 1 g1disk01 and store 2 g2disk01 at time 5h for 45m. 
- 1773429328, ran on quarry2 starting at 2026-03-13 19:15, with 2 simultaneous disk failures on store 3 g1disk01 and store 3 g2disk02 at time 12h for 3h30m; Both disks failed on the same storage server. g2disk02 was successfully fixed after 3h30m, but g1disk01 wasn't and stayed offline for the rest of the experiment. 
- 1773429369, ran on quarry3 starting at 2026-03-13 19:16, with 3 simultaneous disk failures on store 1 g2disk02, store 2 g1disk01 and store 3 g2disk01 at time 10h for 1h30m. 
- 1773429404, ran on quarry4 starting at 2026-03-13 19:16, with 4 simultaneous disk failures on store 1 g1disk01, store 1 g1disk02, store 2 g2disk01 and store 3 g1disk02 at time 7h30m for 30m; g1disk01 on store 1 was not successfully fixed and stayed out of service for the rest of the experiment. 
- 1773680793 ran on quarry starting at 2026-03-16 17:06 with 2 simultaneous disk failures on store 2 g1disk02 and store 3 g2disk01 at time 8h for 2h. 
- 1773680834 ran on quarry2 starting at 2026-03-16 17:07 with 2 simultaneous disk failures on store 1 g2disk01 and store 1 g2disk02 at time 14h for 1h. g2disk02 was not successfully fixed and stayed out of service for the rest of the experiment. 
- 1773680847 ran on quarry3 starting at 2026-03-16 17:07 with 3 simultaneous disk failures on store 1 g1disk01, store 1 g2disk01 and store 2 g2disk02 at time 3h for 2h. g2disk01 on store 1 was not successfully fixed and stayed out of service for the rest of the experiment. 
- 1773680864 ran on quarry4 starting at 2026-03-16 17:07 with 3 simultaneous disk failures on store 2 g1disk02, store 3 g1disk01 and store 3 g2disk02 at time 15h for 45m. g1disk01 on store 3 was not successfully fixed and stayed out of service for the rest of the experiment. 
- 1773680884 ran on quarry5 starting at 2026-03-16 17:08 with 4 simultaneous disk failures on store 1 g1disk02, store 1 g2disk01, store 3 g1disk01 and store 3 g2disk02 at time 6h for 1h15m. g2disk01 on store 1 and g2disk02 on store 3 were not successfully fixed and stayed out of service for the rest of the experiment. 
- 1773680896 ran on quarry7 starting at 2026-03-16 17:08 with 4 simultaneous disk failures on store 1 g2disk02, store 2 g1disk01, store 2 g2disk01 and store 3 g1disk02 at time 11h for 3h. g2disk01 on store 2 was not successfully fixed and stayed out of service for the rest of the experiment. 
- 1773767900 ran on quarry6 starting at 2026-03-17 17:18 with 2 simultaneous disk failures on store 3 g1disk01 for 3h30m and store 3 g2disk02 for 3h40m at time time 12h. Rerun of experiment 1773429328 with 10 min staggered disk fixes and no permanent disk issue. 
- 1773768006 ran on quarry8 starting at 2026-03-17 17:20 with 4 simultaneous disk failures on store 1 g1disk02 for 1h15m, store 1 g2disk01 for 1h25m, store 3 g1disk01 for 1h15m and store 3 g2disk02 for 1h25m at time 6h. Rerun of experiment 1773680884 with 10 min staggered disk fixes and no permanent disk issue. 
- 1775270767, ran on quarry4 starting at 2026-04-04 02:46, with 2 simultaneous disk failures on store 1 g1disk01 for 1h and store 1 g1disk02 for 1h10m at time 13h30m. Staggered fix. 
- 1775270771, ran on quarry5 starting at 2026-04-04 02:46, with 3 simultaneous disk failures on store 1 g1disk02 for 1h50m, store 1 g2disk02 for 2h and store 2 g1disk01 for 1h50m at time 3h30m. Staggered fix. 
- 1775270774, ran on quarry6 starting at 2026-04-04 02:46, with 3 simultaneous disk failures on store 2 g2disk01 for 45m, store 3 g1disk02 for 55m and store 3 g2disk01 for 50m at time 15h30m. Staggered fix. 
- 1775270776, ran on quarry7 starting at 2026-04-04 02:46, with 4 simultaneous disk failures on store 1 g2disk01 for 35m, store 1 g2disk02 for 45m, store 2 g1disk02 for 35m and store 3 g2disk01 for 40m at time 7h. Staggered fix. 
- 1775270779, ran on quarry8 starting at 2026-04-04 02:46, with 4 simultaneous disk failures on store 1 g1disk02 for 2h50m, store 2 g2disk02 for 3h, store 2 g1disk02 for 2h50m and store 3 g1disk01 for 3h10m at time 11h30m. Staggered fix.

### Asynchronous Disk Failure
- 1773429559, ran on quarry5 at 2026-03-13 19:19, with 2 cascading disk failures: g1disk01 on store 1 at time 6h for 1h and g2disk01 on store 2 at time 6h15m for 50m. 
- 1773429588, ran on quarry6 at 2026-03-13 19:19, with 3 cascading disk failures: g1disk01 on store 1 at time 4h for 40m, g1disk02 on store 2 at time 4h8m for 30m, and g2disk01 on store 3 at 4h20m for 55m. g1disk01 on store 1 wasn't fixed and stayed offline for the rest of the experiment. 
- 1773429647, ran on quarry7 at 2026-03-13 19:20, with 2 independent disk failures: g2disk02 on store 1 at time 9h for 1h30m and g1disk01 on store 3 at time 12h for 2h. 
- 1773429670, ran on quarry8 at 2026-03-13 19:21, with 4 rolling disk failures: g2disk01 on store 1 at time 8h for 3h, g1disk01 on store 2 at time 10h for 2h, g2disk02 on store 2 at time 11h30m for 1h15m and g1disk02 on store 3 at time 12h15m for 1h. 
- 1773767292, ran on quarry starting at 2026-03-17 17:08, with 3 cascading disk failures: g2disk01 on store 2 at time 13h for 1h30m, g1disk02 on store 2 at time 13h10m for 1h, and g2disk02 on store 3 at time 13h25m for 1h. 
- 1773767367, ran on quarry2 starting at 2026-03-17 17:09, with 2 rolling disk failures: g1disk02 on store 1 at time 5h for 2h and g2disk01 on store 3 at time 6h30m for 1h30m. 
- 1773767388, ran on quarry3 starting at 2026-03-17 17:09, with 4 rolling disk failures: g2disk01 on store 1 at time 2h for 1h30m, g1disk01 on store 3 at time 3h for 1h, g2disk02 on store 2 at time 3h30m for 2h, and g1disk01 on store 1 at time 4h15m for 1h30m. 
- 1773767435, ran on quarry4 starting at 2026-03-17 17:10, with 2 independent disk failures: g2disk02 on store 3 at time 3h for 45m and g1disk01 on store 2 at time 15h for 1h. 
- 1773767461, ran on quarry5 starting at 2026-03-17 17:11, with 3 independent disk failures: g2disk01 on store 1 at time 2h for 1h, g2disk02 on store 2 at time 7h for 2h, and g1disk02 on store 3 at time 14h for 1h30m. 
- 1773767785, ran on quarry7 starting at 2026-03-17 17:16, with 4 independent disk failures: g1disk02 on store 2 at time 1h30m for 30m, g2disk01 on store 1 at time 5h for 1h15m, g1disk01 on store 3 at time 10h for 45m and g2disk02 on store 3 at time 15h for 2h. 
- 1775167457, ran on quarry starting at 2026-04-02 22:04, with 2 cascading disk failures: g2disk01 on store 3 at time 10h for 1h15m and g1disk02 on store 1 at time 10h12m for 45m.

### Single Server Failure
- 1773946658, ran on quarry starting at 2026-03-19 18:57, with an instant node failure on store 1 at time 6h. Duration was supposed to be 1h30m, but the node unpredictably, litterally failed, and was manually reset at 10:25 the next day. So the total duration is 9h45m. 
- 1774026192, ran on quarry starting at 2026-03-20 17:03, with an instant node failure on store 1 at time 6h for 20m. Rerun of 1773946658 with shorter duration to avoid long failures. 
- 1774026217, ran on quarry2 starting at 2026-03-20 17:03, with an instant node failure on store 2 at time 10h for 15m. 
- 1774132105, ran on quarry starting at 2026-03-21 22:28, with an instant node failure on store 3 at time 3h for 5m. 
- 1774132113, ran on quarry2 starting at 2026-03-21 22:28, with an instant node failure on store 2 at time 14h for 1m. 
- 1774587691, ran on quarry5 starting at 2026-03-27 05:01, with an instant node failure on store 2 at time 7h for 25m. 
- 1774587733, ran on quarry6 starting at 2026-03-27 05:02, with an instant node failure on store 1 at time 30m for 8m. 
- 1775087951, ran on quarry starting at 2026-04-01 23:59, with an instant node failure on store 2 at time 5h for 22m. 
- 1775087960, ran on quarry2 starting at 2026-04-01 23:59, with an instant node failure on store 3 at time 11h for 18m. 
- 1775087966, ran on quarry3 starting at 2026-04-01 23:59, with an instant node failure on store 3 at time 16h for 3m. 
- 1775087972, ran on quarry4 starting at 2026-04-01 23:59, with an instant node failure on store 1 at time 1h30m for 12m.

### Asynchronous Server Failure

- 1773946737, ran on quarry3 starting at 2026-03-19 18:58, with 2 node failures: store 1 at time 4h for 30m and store 2 at time 10h for what was supposed to be 1h, but the node unpredictably failed, and was manually reset at 10:25 the next day, with a total duration of 5h27m. 
- 1774026232, ran on quarry3 starting at 2026-03-20 17:03, with 2 node failures: store 1 at time 4h for 30m and store 2 at time 10h for 25m. Rerun of 1773946737 with shorter duration. 
- 1774026246, ran on quarry4 starting at 2026-03-20 17:04, with 3 node failures: store 1 at time 3h for 20m, store 2 at time 8h for 15m, and store 3 at time 14h for 5m. 
- 1774132120, ran on quarry3 starting at 2026-03-21 22:28, with 2 node failures: store 1 at time 2h for 10m and store 3 at time 7h for 15m. 
- 1774132127, ran on quarry4 starting at 2026-03-21 22:28, with 2 node failures: store 2 at time 6h for 5m, and store 3 at time 13h for 3m. 
- 1774587774, ran on quarry8 starting at 2026-03-27 05:02, with 2 node failures on the same node: store 2 at time 4h for 12m and store 2 at time 11h for 20m. 
- 1775087979, ran on quarry5 starting at 2026-04-01 23:59, with 2 node failures on the same node: store 1 at time 5h for 10m and store 1 at time 14h30m for 15m. 
- 1775087985, ran on quarry6 starting at 2026-04-01 23:59, with 2 node failures: store 3 at time 2h30m for 15m and store 1 at time 12h for 10m. 
- 1775087991, ran on quarry7 starting at 2026-04-01 23:59, with 2 node failures: store 1 at time 8h for 7m and store 3 at time 15h for 18m. 
- 1775087997, ran on quarry8 starting at 2026-04-01 23:59, with 3 node failures: store 2 at time 1h for 5m, store 3 at time 6h30m for 20m, and store 1 at time 13h for 12m. 
- 1775167468, ran on quarry3 starting at 2026-04-02 22:04, with 2 node failures: store 3 at time 9h30m for 6m and store 2 at time 16h for 14m.

### Server Degradation 

- 1774026259, ran on quarry5 starting at 2026-03-20 17:04, with a gradual node failure on store 1 at time 6h for 2h, where delay and loss jump to 100ms and 5% at 25% of the anomaly duration, 300ms and 10% at 50%, and 800ms and 20% at 75%. 
- 1774026268, ran on quarry6 starting at 2026-03-20 17:04, with a gradual node failure on store 2 at time 8h for 3h, where delay and loss jump to 50ms and 2% loss at 20% of the anomaly duration, 150ms and 12% at 40%, 400ms and 12% at 60%, and 1s and 25% at 80%. 
- 1774026280, ran on quarry7 starting at 2026-03-20 17:04, with a linear node failure on store 1 at time 6h for 2h, with a max delay of 500ms and max loss of 15%. 
- 1774132137, ran on quarry5 starting at 2026-03-21 22:28, with a linear node failure on store 2 at time 4h for 1h30m, with a max delay of 200ms and max loss of 8%. 
- 1774132147, ran on quarry6 starting at 2026-03-21 22:29, with a linear node failure on store 1 at time 10h for 4h, with a max delay of 750ms and max loss of 20%. 
- 1774132154, ran on quarry7 starting at 2026-03-21 22:29, with a gradual node failure on store 3 at time 4h for 1h30m, where delay and loss jump to 150ms and 5% at 33% of the anomaly duration, and 500ms and 15% loss at 66%. 
- 1774132163, ran on quarry8 starting at 2026-03-21 22:29, with a gradual node failure on store 2 at time 10h for 4h, where delay and loss jump to 20ms and 1% loss at 10% of the anomaly duration, 80ms and 3% loss at 30%, 200ms and 8% at 50%, 500ms and 15% at 70%, 1s and 30% at 90%. 
- 1774291956, ran on quarry5 starting at 2026-03-23 18:52, with a linear node failure on store 3 at time 5h for 2h, with a max delay of 15ms and a max loss of 4%. 
- 1774291974, ran on quarry6 starting at 2026-03-23 18:52, with a linear node failure on store 2 at time 7h for 3h, with a max delay of 40ms and a max loss of 10%. 
- 1774291987, ran on quarry7 starting at 2026-03-23 18:53, with a gradual node failure on store 1 at time 3h for 2h30m, where delay and loss jump to 3ms and 0.5% at 2% of the anomaly duration, 5ms and 1.5% at 25%, 7ms and 3% at 55% and 10ms and 5% at 85%. 
- 1774292005, ran on quarry8 starting at 2026-03-23 18:53, with a gradual node failure on store 3 at time 9h for 3h, where delay and loss jump to 5ms and 1% at 3% of the anomaly duration, 20ms and 4% at 35% and 35ms and 7% at 70%. 
- 1774479145, ran on quarry starting at 2026-03-25 22:52, with a linear node failure on store 1 at time 2h for 1h, with a max delay of 2ms and a max loss of 1%. 
- 1774479151, ran on quarry2 starting at 2026-03-25 22:52, with a linear node failure on store 2 at time 5h for 2h30m, with a max delay of 4ms and a max loss of 3%. 
- 1774479157, ran on quarry3 starting at 2026-03-25 22:52, with a linear node failure on store 3 at time 11h for 1h30m, with a max delay of 5ms and a max loss of 5%. 
- 1774479161, ran on quarry4 starting at 2026-03-25 22:52, with a linear node failure on store 1 at time 8h for 3h30m, with a max delay of 3ms and a max loss of 2%. 
- 1774478710, ran on quarry5 starting at 2026-03-25 22:45, with a gradual node failure on store 2 at time 3h for 2h, where delay and loss jump to 1ms and 0.5% at 3% of the anomaly duration, and 4ms and 3% at 50%. 
- 1774478725, ran on quarry6 starting at 2026-03-25 22:45, with a gradual node failure on store 3 at time 6h for 1h, where delay and loss jump to 1ms and 0.3% at 2% of the anomaly duration, 3ms and 1.5% at 35%, and 5ms and 4% at 70%. 
- 1774478736, ran on quarry7 starting at 2026-03-25 22:45, with a gradual node failure on store 1 at time 12h for 2h30m, where delay and loss jump to 1ms and 0.5% at 3% of the anomaly duration, 2ms and 1% at 25%, 3ms and 2.5% at 55%, and 5ms and 5% at 80%. 
- 1774478743, ran on quarry8 starting at 2026-03-25 22:45, with a gradual node failure on store 2 at time 5h for 3h, where delay and loss jump to 0.2ms and 0.2% at 2% of the anomaly duration, 0.8ms and 0.8% at 20%, 1.2ms and 1.5% at 40%, 1.4ms and 3% at 65%, and 1.6ms and 4.5% at 90%. 
- 1774586933, ran on quarry starting at 2026-03-27 04:48, with a gradual node failure on store 2 at time 10h for 4h, where delay and loss jump to 0.3ms and 0.1% at 3% of the anomaly duration, 0.5ms and 0.25% at 35%, and 0.7ms and 0.4% at 70%. 
- 1774586939, ran on quarry2 starting at 2026-03-27 04:48, with a gradual node failure on store 3 at time 7h for 6h, where delay and loss jump to 0.1ms and 0.05% at 2% of the anomaly duration, 0.7ms and 0.1% at 25%, 0.5ms and 0.15% at 55%, and 0.8ms and 0.2% at 85%. 
- 1774586951, ran on quarry3 starting at 2026-03-27 04:49, with a linear node failure on store 3 at time 2h for 5h, with a max delay of 1.5ms and a max loss of 0.8%. 
- 1774586961, ran on quarry4 starting at 2026-03-27 04:49, with a linear node failure on store 1 at time 6h for 4h30m, with a max delay of 0.8ms and a max loss of 1%. 
- 1775270759, ran on quarry starting at 2026-04-04 02:45, with a gradual node failure on store 1 at time 4h for 2h, where delay and loss jump to 0.1ms and 0.1% at 3% of the anomaly duration, 0.3ms and 0.3% at 40%, and 0.5ms and 0.5% at 75%. 
- 1775270761, ran on quarry2 starting at 2026-04-04 02:46, with a gradual node failure on store 3 at time 9h for 4h, where delay and loss jump to 0.3ms and 0.2% at 3% of the anomaly duration, 0.7ms and 0.5% at 30%, 0.2ms and 0.1% at 55%, and 0.5ms and 0.4% at 80%. 
- 1775270764, ran on quarry3 starting at 2026-04-04 02:46, with a linear node failure on store 2 at time 5h for 3h, with a max delay of 0.8ms and a max loss of 0%.

### Single Software Node Failure
- 1774656169, ran on quarry starting at 2026-03-28 00:02, with 1 snode killed on store 1 at time 6h for 1h. (broken telemetry)
- 1774656174, ran on quarry2 starting at 2026-03-28 00:02, with 1 snode killed on store 2 at time 9h for 1h30m. (broken telemetry)
- 1774656180, ran on quarry3 starting at 2026-03-28 00:03, with 2 snodes killed on store 1 at time 5h for 45m. (broken telemetry)
- 1774656183, ran on quarry4 starting at 2026-03-28 00:03, with 2 snodes killed on store 3 at time 8h for 1h. (broken telemetry)
- 1774764369, ran on quarry7 starting at 2026-03-29 06:06, with 3 snodes killed on store 2 at time 2h for 30m. (broken telemetry)
- 1774764432, ran on quarry8 starting at 2026-03-29 06:07, with 3 snodes killed on store 3 at time 14h for 45m. (broken telemetry)
- 1774844948, ran on quarry starting at 2026-03-30 04:29, with 1 snode killed on store 1 at time 6h for 1h. 
- 1774844958, ran on quarry2 starting at 2026-03-30 04:29, with 1 snode killed on store 2 at time 9h for 1h30m. 
- 1774844963, ran on quarry3 starting at 2026-03-30 04:29, with 2 snodes killed on store 1 at time 5h for 45m. 
- 1774844969, ran on quarry4 starting at 2026-03-30 04:29, with 2 snodes killed on store 3 at time 8h for 1h. 
- 1774936591, ran on quarry7 starting at 2026-03-31 05:56, with 3 snodes killed on store 2 at time 2h for 30m. 
- 1774936599, ran on quarry8 starting at 2026-03-31 05:56, with 3 snodes killed on store 3 at time 14h for 45m. 
- 1775021366, ran on quarry7 starting at 2026-04-01 05:29, with 1 snode killed on store 3 at time 16h for 20m. 
- 1775021375, ran on quarry8 starting at 2026-04-01 05:29, with 1 snode killed on store 1 at time 3h for 15m. 
- 1775167481, ran on quarry7 starting at 2026-04-02 22:04, with 3 snodes killed on store 1 at time 7h30m for 35m. 
- 1775167484, ran on quarry8 starting at 2026-04-02 22:04, with 2 snodes killed on store 2 at time 12h for 50m.

### Simultaneous Software Node Failure
- 1774656573, ran on quarry5 starting at 2026-03-28 00:09, with simultaneous snode failures: 1 snode killed on store 1 and 1 snode killed on store 2, at time 13h for 1h. (broken telemetry)
- 1774656577, ran on quarry6 starting at 2026-03-28 00:09, with simultaneous snode failures: 1 snode killed on store 1 and 2 snodes killed on store 2, at time 7h for 45m. (broken telemetry)
- 1774764331, ran on quarry5 starting at 2026-03-29 06:05, with simultaneous snode failures: 1 snode killed on store 1 at time 10h for 20m, 1 snode killed on store 2 at time 10h for 25m, and 1 snode killed on store 3 at time 10h for 30m. (broken telemetry)
- 1774764358, ran on quarry6 starting at 2026-03-29 06:05, with simultaneous snode failures: 2 snodes killed on store 1 and 2 snodes killed on store 3, at time 15h for 15m. (broken telemetry)
- 1774844979, ran on quarry5 starting at 2026-03-30 04:29, with simultaneous snode failures: 1 snode killed on store 1 and 1 snode killed on store 2, at time 13h for 1h. 
- 1774844985, ran on quarry6 starting at 2026-03-30 04:29, with simultaneous snode failures: 1 snode killed on store 1 and 2 snodes killed on store 2, at time 7h for 45m. 
- 1774936575, ran on quarry5 starting at 2026-03-31 05:56, with simultaneous snode failures: 1 snode killed on store 1 at time 10h for 20m, 1 snode killed on store 2 at time 10h for 25m, and 1 snode killed on store 3 at time 10h for 30m. 
- 1774936581, ran on quarry6 starting at 2026-03-31 05:56, with simultaneous snode failures: 2 snodes killed on store 1 and 2 snodes killed on store 3, at time 15h for 15m. 
- 1775021334, ran on quarry3 starting at 2026-04-01 05:28, with simultaneous snode failures: 1 snode killed on store 2 and 1 snode killed on store 3, at time 3h30m for 20m. 
- 1775021343, ran on quarry4 starting at 2026-04-01 05:29, with simultaneous snode failures: 1 snode killed on store 1 and 1 snode killed on store 3, at time 11h30m for 15m. 
- 1775021351, ran on quarry5 starting at 2026-04-01 05:29, with simultaneous snode failures: 2 snodes killed on store 1, 1 snode killed on store 2, and 2 snodes killed on store 3, at time 6h for 20m. 
- 1775021360, ran on quarry6 starting at 2026-04-01 05:29, with simultaneous snode failures: 2 snodes killed on store 2 at time 16h30m for 25m and 1 snode killed on store 3 at time 16h30m for 30m. 
- 1775167475, ran on quarry5 starting at 2026-04-02 22:04, with simultaneous snode failures: 3 snodes killed on store 2 at time 14h for 25m and 1 snode killed on store 3 at time 14h for 30m. 
- 1775167478, ran on quarry6 starting at 2026-04-02 22:04, with simultaneous snode failures: 1 snode killed on store 1 and 2 snodes killed on store 3, at time 4h for 40m.

### Asynchonous Software Node Failure
- 1774656607, ran on quarry7 starting at 2026-03-28 00:10, with cascading snode failures: 2 snodes killed on store 1 at time 3h30m for 1h, and 1 snode killed on store 2 at time 4h for 1h. (broken telemetry)
- 1774656595, ran on quarry8 starting at 2026-03-28 00:09, with independent snode failures: 1 snode killed on store 1 at time 5h for 1h, and 2 snodes killed on store 3 at time 11h for 1h30m. (broken telemetry)
- 1774764255, ran on quarry starting at 2026-03-29 06:04, with cascading snode failures: 1 snode killed on store 1 at time 3h for 1h30m, 2 snodes killed on store 2 at time 3h45m for 1h, and 1 snode killed on store 3 at time 4h15m for 35m. (broken telemetry)
- 1774764269, ran on quarry2 starting at 2026-03-29 06:04, with independent snode failures: 3 snodes killed on store 2 at time 4h for 45m, and 2 snodes killed on store 3 at time 13h for 1h10m. (broken telemetry)
- 1774764282, ran on quarry3 starting at 2026-03-29 06:04, with rolling snode failures: 1 snode killed on store 1 at time 9h for 1h30m, 1 snode killed on store 2 at time 11h for 1h20m, and 2 snodes killed on store 3 at time 14h for 1h. (broken telemetry)
- 1774764299, ran on quarry4 starting at 2026-03-29 06:04, with rolling snode failures: 2 snodes killed on store 1 at time 2h for 1h30m, 3 snodes killed on store 2 at time 3h30m for 1h, 1 snode killed on store 3 at time 5h for 2h, and 1 snode killed on store 1 at time 12h for 1h. (broken telemetry)
- 1774844991, ran on quarry7 starting at 2026-03-30 04:29, with cascading snode failures: 2 snodes killed on store 1 at time 3h30m for 1h, and 1 snode killed on store 2 at time 4h for 1h. 
- 1774844998, ran on quarry8 starting at 2026-03-30 04:29, with independent snode failures: 1 snode killed on store 1 at time 5h for 1h, and 2 snodes killed on store 3 at time 11h for 1h30m. 
- 1774936535, ran on quarry starting at 2026-03-31 05:55, with cascading snode failures: 1 snode killed on store 1 at time 3h for 1h30m, 2 snodes killed on store 2 at time 3h45m for 1h, and 1 snode killed on store 3 at time 4h15m for 35m. 
- 1774936551, ran on quarry2 starting at 2026-03-31 05:55, with independent snode failures: 3 snodes killed on store 2 at time 4h for 45m, and 2 snodes killed on store 3 at time 13h for 1h10m. 
- 1774936559, ran on quarry3 starting at 2026-03-31 05:55, with rolling snode failures: 1 snode killed on store 1 at time 9h for 1h30m, 1 snode killed on store 2 at time 11h for 1h20m, and 2 snodes killed on store 3 at time 14h for 1h. 
- 1774936567, ran on quarry4 starting at 2026-03-31 05:56, with rolling snode failures: 2 snodes killed on store 1 at time 2h for 1h30m, 3 snodes killed on store 2 at time 3h30m for 1h, 1 snode killed on store 3 at time 5h for 2h, and 1 snode killed on store 1 at time 12h for 1h. 
- 1775021320, ran on quarry starting at 2026-04-01 05:28, with cascading snode failures: 1 snode killed on store 3 at time 12h for 1h, and 2 snodes killed on store 1 at time 12h45m for 45m. 
- 1775021329, ran on quarry2 starting at 2026-04-01 05:28, with rolling snode failures: 1 snode killed on store 2 at time 5h for 20m, 1 snode killed on store 3 at time 6h for 15m, and 1 snode killed on store 1 at time 7h for 25m. 
- 1775167464, ran on quarry2 starting at 2026-04-02 22:04, with independent snode failures: 2 snodes killed on store 1 at time 2h30m for 40m, and 1 snode killed on store 2 at time 15h for 1h. 
- 1775167472, ran on quarry4 starting at 2026-04-02 22:04, with rolling snode failures: 1 snode killed on store 3 at time 8h for 1h, and 2 snodes killed on store 1 at time 8h30m for 45m.

## Platform Context and Metrics
Scality RING is a distributed object storage system. Data is mapped onto a virtual ring (a distributed hash table) where each software storage node owns a segment of the keyspace and handles reads/writes for objects hashing into that range. Our cluster has 1 supervisor node for management and monitoring, and 3 storage servers each running 6 software storage nodes. Each server has 4 NVMe data disks and 2 SSDs, totaling 12 data disks and 6 SSDs across the cluster. Objects are replicated across different storage nodes for durability.
S3 client traffic enters through an S3 connector running on each storage server. The connector handles S3 protocol and metadata, then routes data operations through the RING's hash table to the storage nodes owning the relevant key ranges. Storage nodes also communicate with each other for replication and internal routing, generating inter-node traffic on top of external S3 I/O. Network and CPU metrics therefore reflect both client-facing work and internal cluster coordination.
When a disk or storage node becomes unavailable, the RING detects that some object replicas are missing and triggers background rebuild tasks to reconstruct them onto healthy disks. Separate background tasks also handle data integrity repair (fixing corrupted or inconsistent chunks) and rebalancing (redistributing data when disk usage is uneven, typically after recovery). Capacity metrics distinguish between logical data size, replicated data size, and actual disk usage which includes storage overhead.

### Platform level metrics:
Cluster-wide aggregate metrics across all 3 storage servers as well as the Supervisor server. It is important to note that the experiment runs on the Supervisor, and as such is integrated into some of the platform metrics. However its impact is virtually the same across all experiments.

- cpu_usage_ratio: (ratio) (0-1) Fraction of CPU time not idle averaged across all servers.
- cpu_load_ratio: (ratio) (>= 0) CPU load average across all servers and normalized by CPU count. Can exceed 1.0 when the run queue is longer than the CPU count.
- memory_usage_ratio: Ratio (0-1) Fraction of total used memory averaged across all servers.
- network_in_bytes: (bytes/s) Sum of incoming network throughput across all network interfaces on all servers (includes S3 traffic, inter-node system traffic, etc.)
- network_out_bytes: (bytes/s) Sum of outgoing network throughput across all network interfaces on all servers (includes S3 traffic, inter-node system traffic, etc.)
- objects_count: (count) Number of objects stored on the RING, including replicas.
- objects_unique_count: (count) Number of unique objects stored on the RING, deduplicated to count only logical objects regardless of replica count.
- objects_missing_count: (count) Number of objects with missing or OOS chunks.
- capacity_disk_unique_tb: (TB) Total stored data of unique objects (before replication). Reflects "logical" data size.
- capacity_disk_stored_tb: (TB) Total stored data including replicas.
- capacity_disk_used_tb: (TB) Total actual disk space consumed, including various overheads beyond stored object sizes.
- capacity_disk_available_tb: (TB) Total free disk space on the RING.
- capacity_disk_total_tb: (TB) Total physical disk capacity. Static unless disks are removed from the RING.
- disk_read_bytes: (bytes/s) Total disk read throughput summed across all disks.
- disk_write_bytes: (bytes/s) Total disk write throughput summed across all disks.
- disk_io_time_seconds: (s/s) (0-1) Fraction of time spent on I/O averaged across all disks. A value of 1.0 implies a device spent 100% of its time doing I/O (fully saturated).

### Application-level metrics
Application-level metrics measuring the S3 storage service through which all experiment traffic flows. Measured at the nginx reverse proxy level on each storage server and aggregated across the cluster. Explanation of sometimes missing metrics

- s3_errors_5xx: (errors/s) Rate of HTTP 5xx server errors across all S3 services.
- s3_request_get_operations: (ops/s) GET request rate.
- s3_request_put_operations: (ops/s) PUT request rate.
- s3_request_delete_operations: (ops/s) DELETE request rate.
- s3_request_head_operations: (ops/s) HEAD request rate (metadata lookups).
- s3_request_post_operations: (ops/s) POST request rate (near constant since we are not using multipart uploads in our nominal workload).
- s3_throughput_in_bytes: (bytes/s) Client-to-S3 data rate.
- s3_throughput_out_bytes: (bytes/s) S3-to-client data rate (dominates throughput_in in our GET heavy nominal workload).
- s3_request_get_latency: (seconds) 95th percentile GET request duration.
- s3_request_put_latency: (seconds) 95th percentile PUT request duration.
- s3_request_delete_latency: (seconds) 95th percentile DELETE request duration.
- s3_request_head_latency: (seconds) 95th percentile HEAD request duration.
- s3_request_post_latency: (seconds) 95th percentile POST request duration. Near-constant in our nominal workload.

### Server-level metrics (x3)
Per-server metrics for each of the 3 storage servers (prefixed store1-, store2-, store3-). Combines OS-level metrics (CPU, memory, network) with RING system level metrics (operations, latency, throughput, errors, background tasks).

- cpu_usage_ratio: (ratio) (0-1) Fraction of CPU time not idle for this server.
- cpu_load_ratio: (ratio) (>= 0) CPU load average normalized by CPU count for this server. Can exceed 1.0 under saturation.
- memory_usage_ratio: (ratio) (0-1) Fraction of total used memory for this server.
- network_in_bytes: (bytes/s) ALL inncoming network throughput for this server, including S3 client traffic, RING inter-node traffic, monitoring, etc.
- network_out_bytes: (bytes/s) ALL outgoing network throughput for this server, including S3 client traffic, RING inter-node traffic, monitoring, etc.
- operations_sent: (ops/s) Rate of internal RING operations this server sends to other servers.
- operations_received: (ops/s) Rate of internal RING operations this server receives from other servers.
- latency_sent_milliseconds: (ms) Average round-trip time for RING operations this server sends.
- latency_received_milliseconds: (ms) Average local processing time for RING operations this server receives.
- throughput_sent_bytes: (bytes/s) Data payload (object chunks) sent by this server via RING operations.
- throughput_received_bytes: (bytes/s) Data payload received by this server via RING operations.
- errors_sent: (errors/s) Rate of failed outbound RING operations.
- errors_received: (errors/s) Rate of failed inbound RING operations.
- rebuild_scanned_tasks: (tasks/s) Rate of rebuild scanning. Rebuild reconstructs missing data replicas.
- rebuild_rebuilt_tasks: (tasks/s) Rate of chunks actually rebuilt.
- repair_scanned_tasks: (tasks/s) Rate of repair scanning. Fixes data integrity issues (corrupted chunks, checksum mismatches).
- repair_repaired_tasks: (tasks/s) Rate of chunks actually repaired.
- balance_scanned_tasks: (tasks/s) Rate of balance scanning. Redistributes data when disk usage is uneven. May activate after disk failure recovery.
- balance_balanced_tasks: (tasks/s) Rate of chunks actually rebalanced.

### Device-level metrics (x7)
Per-disk metrics for each physical disk on each storage server. Column naming follows the pattern {server}-{device}-{metric} (e.g. store1-g1disk01-disk_read_bytes). Each server has 7 devices:

- g1disk01, g1disk02, g2disk01, g2disk02: NVMe data disks, where RING object data is stored. These are the disks targeted by disk failure anomalies.
- ssd01, ssd02: SSDs used for S3 metadata and small object storage 
- root: OS root disk (/). Not a storage disk, but reflects system-level activity.

The metrics for devices are:

- disk_read_bytes: (bytes/s) Disk read throughput.
- disk_write_bytes: (bytes/s) Disk write throughput.
- disk_io_time_seconds: (s/s) (0–1) Fraction of time spent on I/O. A value approaching 1.0 implies the disk is saturated.
- disk_usage_ratio: (ratio) (0–1) Disk space space utilization.


# Code
## Accessing the XML knowledge
The code in `Scripts/queryXML` shows examples of how to query and explore the XML files generated for each time series in SHAD.

Each XML file contains structured information about:
- dataset-level metadata (id, anomaly presence, type, criticality)
- per-dimension metrics
- anomaly events with temporal and structural information
- relationships between affected dimensions

---

The script provides, for a given time series, an example of how to (i) retrieve the global information, (ii) extract all the metric names, (iii) get all dimensions affected by an anomaly on a given store, (iv) get info of the degradation (if present) for a particular dimension, and (v) get all the dimensions affected by the same anomaly of the analyzed one. 

##  TS Representations
The codes in `Scripts/generate_images` and `Scripts/compute_features` allows to generate the time series image and catch22 representations, respectively.  The codes' outputs are stored in the Representation folder. For images, there is a single png image per time series, while all the catch22 features are stored in a single CSV file. These representations are then used for the LLM interpretability experiment. 

## Anomaly Detection
For the implementation of anomaly detectors, we refer the readers to the [TSB-AD](https://github.com/TheDatumOrg/TSB-AD) benchmark. 

## Interpretability
The code in `Scripts/interpretability_main` runs the interpretability experiment for the 3 different types of representations. To run the experiment, it is necessary to store the MISTRAL API key in a .env file (MISTRAL_API_KEY=XXX) that is then loaded in the experiment script. 
