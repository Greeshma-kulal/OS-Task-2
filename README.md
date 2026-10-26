# OS Synchronization Assignment

Python implementations of the Readers–Writers and Dining Philosophers problems using semaphore-based and monitor-style synchronization. The programs record execution events and generate HTML pages that replay those recorded events.

## Implementations

- Readers–Writers using semaphores
- Readers–Writers using monitor-style synchronization (`threading.Condition`)
- Dining Philosophers using semaphores
- Dining Philosophers using monitor-style synchronization

## Screenshots

Screenshots of terminal output and HTML playback are stored in [`screenshots/`](screenshots/).

### Readers–Writers: Semaphore-Based

**Terminal output**

![Readers–Writers semaphore terminal output](screenshots/readers_writers_semaphore_terminal.png)

**HTML animation**

![Readers–Writers semaphore animation](screenshots/readers_writers_semaphore_animation.png)

### Readers–Writers: Monitor-Based

**HTML animation**

![Readers–Writers monitor animation](screenshots/readers_writers_monitor_animation.png)

**Terminal output**

![Readers–Writers monitor animation](screenshots/readers_writers_monitor_terminal.png)

### Dining Philosophers: Semaphore-Based

**Terminal output — Part 1**

![Dining Philosophers semaphore terminal output part 1](screenshots/dining_philosophers_semaphore_terminal_part1.png)

**Terminal output — Part 2**

![Dining Philosophers semaphore terminal output part 2](screenshots/dining_philosophers_semaphore_terminal_part2.png)

**HTML animation**

![Dining Philosophers semaphore animation](screenshots/dining_philosophers_semaphore_animation.png)

### Dining Philosophers: Monitor-Based

**Terminal output**

![Dining Philosophers monitor terminal output](screenshots/dining_philosophers_monitor_terminal.png)

**HTML animation**

![Dining Philosophers monitor animation](screenshots/dining_philosophers_monitor_animation.png)

## Project Structure

```text
OS-Synchronization-Assignment/
├── README.md
├── screenshots/
│   ├── README.md
│   └── terminal and HTML animation screenshots
├── readers_writers/
├── dining_philosophers/
└── generated_html/
```

## Notes

- The HTML pages replay events recorded during a completed Python execution; they do not control live Python threads.
- Event ordering can vary between runs because of thread scheduling and delays.
- Run the relevant Python program again to generate a fresh event trace and HTML replay.
