"""
utils/projects.py
-----------------
Project Ideas Engine — maps COCO-detected objects to STEM project suggestions
tailored for students ages 9-13, using only common household items.

Every project connects to Science, Technology, Engineering, or Math concepts
that align with middle-school curriculum standards.

PUBLIC API
----------
  PROJECT_MAP  : dict[str, list[dict]]  — per-class STEM project ideas
  COMBO_MAP    : dict[frozenset, dict]  — bonus projects for 2+ objects together
  get_project_suggestions(detected_names, max_results) -> list[dict]

Project dict schema
-------------------
  title       : str          — short descriptive name
  emoji       : str          — single representative emoji
  difficulty  : str          — "Easy" | "Medium" | "Hard"
  time_est    : str          — e.g. "25 mins"
  stem_tag    : str          — "Science" | "Engineering" | "Technology" | "Math"
  tagline     : str          — punchy hook sentence mentioning the STEM concept
  steps       : List[str]   — 4-5 clear steps a student can follow independently
  materials   : List[str]   — only common household items + the detected object
  learn       : str          — "You'll learn about X by doing this."
"""

from __future__ import annotations

from typing import List

# ─────────────────────────────────────────────────────────────────────────────
# PROJECT_MAP  –  STEM projects for every PREFERRED_CLASS
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_MAP: dict[str, list[dict]] = {

    "cup": [
        {
            "title": "Sound Wave Visualizer",
            "emoji": "🔊",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "stem_tag": "Science",
            "tagline": "Discover how sound waves travel through matter by making sand dance on a cup!",
            "steps": [
                "Stretch plastic wrap tightly over the top of a cup and secure with a rubber band.",
                "Sprinkle a small pinch of salt or sand on the plastic wrap surface.",
                "Hold the cup near a speaker or place it next to your mouth and hum loudly.",
                "Watch the salt grains jump and form patterns from the vibrations.",
                "Try different pitches — high vs. low — and record which moves the salt more.",
            ],
            "materials": ["cup", "plastic wrap", "rubber band", "salt", "speaker or voice"],
            "learn": "You'll learn about how sound waves transfer energy through vibrating matter.",
        },
        {
            "title": "Water Density Tower",
            "emoji": "🌈",
            "difficulty": "Medium",
            "time_est": "25 mins",
            "stem_tag": "Science",
            "tagline": "Stack five colorful liquids that refuse to mix — science explains why!",
            "steps": [
                "Gather 5 cups and fill each with: corn syrup, dish soap, water, vegetable oil, and rubbing alcohol.",
                "Add a different food coloring to each cup to tell them apart.",
                "Slowly pour each liquid one at a time down the side of a tall clear cup, starting with corn syrup.",
                "Watch each layer float on top of the denser one below without mixing.",
                "Measure the height of each layer with a ruler and rank liquids from densest to least dense.",
            ],
            "materials": ["cup", "corn syrup", "dish soap", "water", "vegetable oil", "food coloring", "ruler"],
            "learn": "You'll learn about density — why liquids with more mass per volume sink below lighter ones.",
        },
        {
            "title": "Paper Cup Trebuchet",
            "emoji": "⚔️",
            "difficulty": "Hard",
            "time_est": "45 mins",
            "stem_tag": "Engineering",
            "tagline": "Engineer a medieval siege weapon scaled to a cup — measure how far it launches!",
            "steps": [
                "Tape two pencils upright as support towers on a flat base (book or cardboard).",
                "Balance a ruler across the tops so it pivots like a seesaw.",
                "Tape a cup to the short end of the ruler and a bag of coins to the long end as counterweight.",
                "Load a small ball of foil into the cup, hold the cup end down, then release.",
                "Measure launch distance, adjust counterweight mass, and record whether heavier = farther.",
            ],
            "materials": ["cup", "ruler", "pencils", "tape", "coins", "cardboard", "foil"],
            "learn": "You'll learn about levers, counterweights, and how potential energy converts to kinetic energy.",
        },
    ],

    "bottle": [
        {
            "title": "Air Pressure Rocket",
            "emoji": "🚀",
            "difficulty": "Medium",
            "time_est": "25 mins",
            "stem_tag": "Engineering",
            "tagline": "Engineer a pressurized rocket and test how launch angle changes flight distance!",
            "steps": [
                "Fill a plastic bottle 1/3 full with water.",
                "Cut fins from cardboard and tape them symmetrically around the bottle neck.",
                "Take outside and prop the bottle at 45° against a wall or fence.",
                "Stomp the bottle hard and fast — pressurized water launches it skyward.",
                "Try angles of 30°, 45°, and 60° and measure landing distances to find the optimum.",
            ],
            "materials": ["bottle", "water", "cardboard", "tape", "ruler"],
            "learn": "You'll learn about air pressure and how launch angle affects projectile range.",
        },
        {
            "title": "Bernoulli Levitator",
            "emoji": "🌬️",
            "difficulty": "Easy",
            "time_est": "10 mins",
            "stem_tag": "Science",
            "tagline": "Suspend a ping-pong ball in mid-air using only airflow — Bernoulli's principle in action!",
            "steps": [
                "Cut the bottom off a plastic bottle so it forms a funnel shape.",
                "Place a small foil ball or crumpled paper ball inside the wide opening.",
                "Blow steadily through the narrow neck — the ball floats and won't fall out!",
                "Tilt the bottle sideways and observe — does the ball stay suspended?",
                "Try balls of different weights and record which ones the airstream can hold.",
            ],
            "materials": ["bottle", "scissors", "foil", "paper"],
            "learn": "You'll learn about Bernoulli's principle — faster-moving air creates lower pressure that lifts objects.",
        },
        {
            "title": "Ecosystem in a Bottle",
            "emoji": "🌍",
            "difficulty": "Hard",
            "time_est": "40 mins + observe 2 weeks",
            "stem_tag": "Science",
            "tagline": "Build a self-sustaining mini-ecosystem and observe the water cycle happening inside!",
            "steps": [
                "Add 3 cm of small rocks to the bottom of a large clear bottle for drainage.",
                "Add 5 cm of soil on top of the rocks.",
                "Plant two or three small plants or seedlings and water gently.",
                "Seal the top with plastic wrap secured by a rubber band.",
                "Place in indirect sunlight and observe daily — record condensation, plant growth, and any changes.",
            ],
            "materials": ["bottle", "soil", "small rocks", "seedlings", "water", "plastic wrap", "rubber band"],
            "learn": "You'll learn about the water cycle, photosynthesis, and how closed ecosystems sustain themselves.",
        },
    ],

    "book": [
        {
            "title": "Bridge Load Test",
            "emoji": "🌉",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Engineering",
            "tagline": "Stack books as towers and engineer a paper bridge — then test how much weight it holds!",
            "steps": [
                "Stack two equal piles of books about 15 cm apart to act as bridge supports.",
                "Fold a single sheet of paper into a corrugated (accordion) shape and lay it across the gap.",
                "Stack coins one at a time in the centre and count how many the bridge holds before collapsing.",
                "Rebuild using 2 sheets folded differently (tube shape, arch) and repeat the test.",
                "Record results in a table — which shape held the most weight per gram of paper?",
            ],
            "materials": ["book", "paper", "coins", "ruler"],
            "learn": "You'll learn about structural engineering — how shape and form distribute load more than material alone.",
        },
        {
            "title": "Book Spine Barcode Decoder",
            "emoji": "📊",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Technology",
            "tagline": "Decode real barcodes from books and discover the math hidden in every ISBN!",
            "steps": [
                "Pick 5 books and write down their 13-digit ISBN from the back cover barcode.",
                "Look up the ISBN-13 check digit algorithm: multiply digits alternately by 1 and 3.",
                "Sum all the products, divide by 10, and see if the remainder matches the last digit.",
                "Try the same formula on a barcode you find on a cereal box or shampoo bottle.",
                "Record which barcodes pass and which fail — what does a failed check digit mean?",
            ],
            "materials": ["book", "pencil", "paper", "calculator"],
            "learn": "You'll learn about check-digit algorithms — the math that detects errors in scanned barcodes.",
        },
        {
            "title": "Friction Ramp Experiment",
            "emoji": "📐",
            "difficulty": "Medium",
            "time_est": "25 mins",
            "stem_tag": "Science",
            "tagline": "Use stacked books as a ramp and measure how surface type changes friction force!",
            "steps": [
                "Stack books to create a ramp at 30°, 45°, and 60° angles.",
                "Slide the same small object (eraser, block) down the ramp covered with different surfaces: bare book cover, paper, fabric, foil.",
                "Time each slide with a stopwatch and record the results.",
                "Calculate which surface slows the object most — that has the most friction.",
                "Graph angle vs. time for each surface type.",
            ],
            "materials": ["book", "eraser", "fabric", "foil", "paper", "stopwatch"],
            "learn": "You'll learn about friction — how surface texture and angle both affect an object's resistance to sliding.",
        },
    ],

    "chair": [
        {
            "title": "Pendulum Painting Machine",
            "emoji": "🎨",
            "difficulty": "Medium",
            "time_est": "35 mins",
            "stem_tag": "Math",
            "tagline": "Hang a swinging pendulum from a chair and let math create perfect symmetrical patterns!",
            "steps": [
                "Tie a string from the top rung of a chair, hanging a cup with a pinhole bottom.",
                "Fill the cup with paint thinned with water.",
                "Hold a large sheet of paper under the cup, pull the pendulum sideways, and release.",
                "Watch it swing and drip a symmetrical pattern onto the paper.",
                "Change string length and observe how the period (swing time) changes — measure with a stopwatch.",
            ],
            "materials": ["chair", "string", "cup", "paint", "water", "paper", "stopwatch"],
            "learn": "You'll learn about pendulum period — how string length (not mass) controls how fast a pendulum swings.",
        },
        {
            "title": "Pulley System Builder",
            "emoji": "⚙️",
            "difficulty": "Hard",
            "time_est": "40 mins",
            "stem_tag": "Engineering",
            "tagline": "Rig a simple pulley over a chair back and measure how it reduces the force needed to lift things!",
            "steps": [
                "Thread a string over a round smooth object (like a thread spool) tied to a chair back.",
                "Attach a bag of books to one end as the load and a bag of coins to the other as effort.",
                "Measure the weight of the load with a rubber band stretched as a scale.",
                "Count how many coins balance the load with 1, 2, and 3 pulley loops.",
                "Calculate the mechanical advantage: load weight ÷ effort weight.",
            ],
            "materials": ["chair", "string", "books", "coins", "rubber band", "bag"],
            "learn": "You'll learn about mechanical advantage — how pulleys multiply force so you lift more with less effort.",
        },
    ],

    "laptop": [
        {
            "title": "Reaction Time Tester",
            "emoji": "⚡",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Measure your brain's reaction speed in milliseconds using just a ruler!",
            "steps": [
                "Open a free online reaction time test in a browser, OR use the ruler drop method.",
                "For the ruler method: partner holds a 30 cm ruler vertically, you position fingers at the zero mark.",
                "Partner drops without warning — catch it as fast as you can and read the cm mark.",
                "Use the formula: time (s) = √(2 × distance_in_metres / 9.8) to convert cm to milliseconds.",
                "Test 10 times, record each, calculate your average, and compare dominant vs. non-dominant hand.",
            ],
            "materials": ["laptop", "ruler", "paper", "pencil"],
            "learn": "You'll learn about reaction time and how to use physics formulas to convert measurements into time.",
        },
        {
            "title": "Binary Code Translator",
            "emoji": "💾",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Technology",
            "tagline": "Decode how computers store letters as 1s and 0s — then write your name in binary!",
            "steps": [
                "Look up the ASCII table online — each letter maps to a number (A=65, B=66 …).",
                "Convert your first name's letters to their ASCII numbers.",
                "Convert each number to 8-bit binary (e.g. 65 → 01000001) by dividing by 2 repeatedly.",
                "Write your full name in binary on paper.",
                "Trade with a partner and decode each other's binary names.",
            ],
            "materials": ["laptop", "paper", "pencil"],
            "learn": "You'll learn about binary number systems — the base-2 code that underpins all digital information.",
        },
        {
            "title": "Weather Data Grapher",
            "emoji": "🌤️",
            "difficulty": "Hard",
            "time_est": "45 mins",
            "stem_tag": "Math",
            "tagline": "Collect 7 days of real weather data and build a graph that reveals hidden patterns!",
            "steps": [
                "Use a weather website to record today's temperature, humidity, and wind speed.",
                "Do this every day for 7 days and log all values in a table on paper.",
                "Draw a multi-line graph with days on the x-axis and each measurement on the y-axis.",
                "Identify the range, mean, and median for each variable.",
                "Write two observations about patterns you see between the variables.",
            ],
            "materials": ["laptop", "paper", "pencil", "ruler", "coloured pens"],
            "learn": "You'll learn about data collection, statistical measures, and how to read trends in line graphs.",
        },
    ],

    "cell phone": [
        {
            "title": "Smartphone Spectrometer",
            "emoji": "🌈",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Science",
            "tagline": "Turn your phone into a spectrometer that splits light into its colours using a DVD!",
            "steps": [
                "Cut a narrow slit (3 mm wide) in a piece of dark card.",
                "Cut a small square from an old CD or DVD — this is your diffraction grating.",
                "Tape the card slit over the phone camera and angle the CD piece at 45° in front of it.",
                "Point the slit at different light sources: sunlight, LED, fluorescent bulb, candle.",
                "Photograph each spectrum and compare the colour bands — are they the same width?",
            ],
            "materials": ["cell phone", "dark card", "scissors", "tape", "old CD or DVD"],
            "learn": "You'll learn about light spectra — how different light sources emit different wavelengths of colour.",
        },
        {
            "title": "Slow-Motion Physics Lab",
            "emoji": "🎥",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Use your phone's slow-motion camera to measure gravity — with just a dropped ball!",
            "steps": [
                "Set your phone to slow-motion video mode (120fps or higher).",
                "Hold a small object (coin or eraser) at a known height (e.g. 1 metre) next to a ruler taped to a wall.",
                "Drop the object and film it falling past the ruler.",
                "Count the frames it takes to fall and convert to seconds (frames ÷ fps).",
                "Calculate gravity: g = 2h / t² and compare to 9.8 m/s² — how close did you get?",
            ],
            "materials": ["cell phone", "coin", "ruler", "tape"],
            "learn": "You'll learn how to measure gravitational acceleration using frame-by-frame video analysis.",
        },
        {
            "title": "Decibel Mapping Survey",
            "emoji": "📊",
            "difficulty": "Medium",
            "time_est": "35 mins",
            "stem_tag": "Math",
            "tagline": "Map the noise levels in your home and discover which rooms are loudest — with real data!",
            "steps": [
                "Install a free decibel meter app on the phone.",
                "Visit 8 locations in your home (kitchen, bathroom, bedroom, outside, etc.).",
                "Record 3 readings per location and calculate the average.",
                "Draw a floor plan of your home and label each room with its average decibel level.",
                "Identify the loudest and quietest spots and hypothesize why.",
            ],
            "materials": ["cell phone", "paper", "pencil", "ruler"],
            "learn": "You'll learn about the decibel scale — a logarithmic measure of sound intensity.",
        },
    ],

    "keyboard": [
        {
            "title": "Typing Speed vs. Accuracy Experiment",
            "emoji": "📈",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Math",
            "tagline": "Run a real experiment: does typing faster always hurt accuracy? Graph the results!",
            "steps": [
                "Open any free online typing test (e.g. typing.com) or use a stopwatch with a fixed text passage.",
                "Type the same 50-word passage 5 times at your natural speed, recording WPM and errors each time.",
                "Now try typing 20% faster deliberately — record the error rate.",
                "Plot WPM on the x-axis and error count on the y-axis on a scatter plot.",
                "Draw a line of best fit and describe the relationship you observe.",
            ],
            "materials": ["keyboard", "laptop", "paper", "pencil", "ruler"],
            "learn": "You'll learn about the speed-accuracy trade-off and how to create and interpret scatter plots.",
        },
        {
            "title": "Circuit Keyboard Hack",
            "emoji": "🔌",
            "difficulty": "Hard",
            "time_est": "50 mins",
            "stem_tag": "Technology",
            "tagline": "Discover how keyboard circuits work by mapping which keys share the same electrical row!",
            "steps": [
                "Carefully unscrew and open an old USB keyboard (ask permission first).",
                "Locate the flexible circuit sheets inside — note rows and columns.",
                "Use a 9V battery and small LED: touch the two wires to different circuit traces to find which light up.",
                "Draw a grid map of which keys connect to which row/column traces.",
                "Explain in writing how a matrix scan works and why keyboards need fewer wires than keys.",
            ],
            "materials": ["keyboard", "9V battery", "LED", "wire", "screwdriver", "paper", "pencil"],
            "learn": "You'll learn about matrix circuits — how keyboards detect keypresses using a grid of rows and columns.",
        },
    ],

    "mouse": [
        {
            "title": "Optical Sensor Dissection",
            "emoji": "🔬",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Technology",
            "tagline": "Crack open an old mouse and discover the tiny camera that tracks your every movement!",
            "steps": [
                "Unscrew an old optical mouse (ask permission) and remove the casing.",
                "Locate the small LED and the sensor chip directly below it.",
                "Shine a flashlight at the sensor area and look for the reflected light pattern.",
                "Move the mouse slowly and watch how the LED illuminates the surface for the camera.",
                "Sketch the internal components and label: LED, sensor, scroll encoder, circuit board.",
            ],
            "materials": ["mouse", "screwdriver", "flashlight", "paper", "pencil"],
            "learn": "You'll learn how optical sensors use reflected light to detect motion — the same principle as cameras.",
        },
        {
            "title": "Friction Surface Science Test",
            "emoji": "📏",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Slide your mouse across 5 surfaces and calculate which has the lowest coefficient of friction!",
            "steps": [
                "Attach a rubber band to the front of your mouse as a force measurer.",
                "Pull the mouse at a constant slow speed across 5 surfaces: bare desk, paper, fabric, foil, cardboard.",
                "Stretch the rubber band and estimate force by how far it stretches (1 cm = 1 unit).",
                "Record force for each surface in a table.",
                "Rank the surfaces from lowest to highest friction — which would make the best mouse pad?",
            ],
            "materials": ["mouse", "rubber band", "paper", "fabric", "foil", "cardboard", "ruler"],
            "learn": "You'll learn about friction force and how different surface textures create more or less resistance.",
        },
    ],

    "remote": [
        {
            "title": "Infrared Light Detector",
            "emoji": "📡",
            "difficulty": "Easy",
            "time_est": "10 mins",
            "stem_tag": "Science",
            "tagline": "Make invisible infrared light visible using just your phone camera — technology revealed!",
            "steps": [
                "Open your phone's front-facing camera and point a TV remote at the lens.",
                "Press any button on the remote while watching the phone screen.",
                "See the purple-white flash? That's infrared light invisible to your eyes but not the camera!",
                "Try the same with the rear camera — does it show the IR flash? (Most rear cameras filter it out.)",
                "Hold coloured transparent materials (sweet wrappers) in front — which block IR light?",
            ],
            "materials": ["remote", "cell phone"],
            "learn": "You'll learn that IR light sits beyond visible spectrum and how silicon sensors detect wavelengths human eyes cannot.",
        },
        {
            "title": "Signal Strength Mapping",
            "emoji": "📶",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Technology",
            "tagline": "Map how walls, distance, and objects weaken your remote's signal — real wireless science!",
            "steps": [
                "Stand 1 m from your TV and confirm the remote works — that's your baseline.",
                "Move 1 m further back each time and record the farthest distance the remote still works.",
                "Now test signal through 1, 2, and 3 layers of different materials: fabric, cardboard, foil.",
                "Record which materials block the signal completely vs. partially.",
                "Draw a signal map showing which angles and distances work best.",
            ],
            "materials": ["remote", "tv", "ruler", "fabric", "cardboard", "foil", "paper", "pencil"],
            "learn": "You'll learn how IR signals weaken with distance (inverse square law) and how materials absorb radiation.",
        },
    ],

    "clock": [
        {
            "title": "Pendulum Clock Builder",
            "emoji": "⏱️",
            "difficulty": "Medium",
            "time_est": "35 mins",
            "stem_tag": "Engineering",
            "tagline": "Build a real pendulum and tune it to tick exactly once per second — just like a grandfather clock!",
            "steps": [
                "Tie a washer or coins to the end of a 25 cm string.",
                "Hang it from a fixed point (top of a door frame or shelf edge).",
                "Pull the pendulum sideways 5° and release — time 10 full swings with a stopwatch.",
                "Divide by 10 to get the period. Adjust string length until the period is exactly 1 second.",
                "Use the formula L = g × T² / (4π²) to calculate the theoretical length and compare.",
            ],
            "materials": ["clock", "string", "washers or coins", "stopwatch", "ruler", "tape"],
            "learn": "You'll learn about pendulum physics — how string length alone determines the period of oscillation.",
        },
        {
            "title": "Circadian Rhythm Log",
            "emoji": "🧬",
            "difficulty": "Easy",
            "time_est": "10 mins/day for 5 days",
            "stem_tag": "Science",
            "tagline": "Track your own body clock over 5 days and find the pattern in your energy levels!",
            "steps": [
                "Set 4 alarms per day: morning, noon, afternoon, evening.",
                "At each alarm, rate your energy 1–10 and record heart rate (count beats for 15 s × 4).",
                "Log data for 5 days in a table.",
                "Plot each day's energy and heart rate on the same graph.",
                "Identify your peak energy time and whether your rhythm shifts on weekends.",
            ],
            "materials": ["clock", "paper", "pencil"],
            "learn": "You'll learn about circadian rhythms — the 24-hour biological cycle that governs energy, sleep, and focus.",
        },
        {
            "title": "Sundial Calibration Challenge",
            "emoji": "☀️",
            "difficulty": "Medium",
            "time_est": "20 mins + check every hour",
            "stem_tag": "Math",
            "tagline": "Build a sundial and compare it to a clock — discovering why time zones exist!",
            "steps": [
                "Push a pencil through the centre of a paper plate at a 40° angle (matching your latitude).",
                "Place outside in a sunny spot and mark the shadow position each hour, labelling the time.",
                "Compare your sundial reading to the clock every hour for a full day.",
                "Research why sundials and clocks differ (solar vs. clock time, time zones, equation of time).",
                "Calculate the average difference in minutes between solar and clock time at your location.",
            ],
            "materials": ["clock", "paper plate", "pencil", "marker", "tape"],
            "learn": "You'll learn why time zones were invented and how solar noon differs from clock noon depending on longitude.",
        },
    ],

    "backpack": [
        {
            "title": "Ergonomic Load Experiment",
            "emoji": "⚖️",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Science",
            "tagline": "Measure how backpack weight and position affect your posture and breathing — real biomechanics!",
            "steps": [
                "Stand straight against a wall and have a partner trace your natural posture outline on paper.",
                "Load the backpack with 10% of your body weight — wear it and trace again.",
                "Increase to 20% and 30% of body weight and trace each time.",
                "Count your breaths per minute at each load using the clock.",
                "Compare posture outlines side by side and record at what weight your posture noticeably changes.",
            ],
            "materials": ["backpack", "clock", "books", "paper", "pencil"],
            "learn": "You'll learn about center of gravity and how uneven loads shift your spine's posture alignment.",
        },
        {
            "title": "Insulation Efficiency Tester",
            "emoji": "🌡️",
            "difficulty": "Hard",
            "time_est": "45 mins",
            "stem_tag": "Engineering",
            "tagline": "Engineer the best insulating layer for your backpack by testing which material slows heat loss most!",
            "steps": [
                "Fill a zip-lock bag with hot water from the tap (not boiling) and seal tightly.",
                "Wrap the bag in one layer of a test material: newspaper, fabric, foil, cardboard, or nothing.",
                "Place inside the backpack pocket and measure the temperature every 5 minutes for 20 minutes.",
                "Repeat with each material and plot temperature vs. time on the same graph.",
                "Calculate the rate of cooling (°C per minute) for each material and rank them.",
            ],
            "materials": ["backpack", "zip-lock bag", "water", "thermometer", "newspaper", "fabric", "foil", "cardboard", "clock"],
            "learn": "You'll learn about thermal insulation — how different materials slow the transfer of heat energy.",
        },
    ],

    "teddy bear": [
        {
            "title": "Center of Gravity Hunt",
            "emoji": "⚖️",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Find the exact invisible point where your teddy bear balances — that's its center of gravity!",
            "steps": [
                "Hold your teddy bear by one paw and let it hang freely — tie a string to mark the vertical line.",
                "Repeat from two other hanging points, each time drawing the vertical plumb line with chalk.",
                "The point where all three lines cross is the center of gravity.",
                "Test: balance the bear on a pencil placed at that exact point.",
                "Try removing the stuffing from one arm — does the center of gravity shift? Test and record.",
            ],
            "materials": ["teddy bear", "string", "chalk or marker", "pencil"],
            "learn": "You'll learn about center of gravity — the single point where an object's weight is perfectly balanced.",
        },
        {
            "title": "Stuffing Compression Science",
            "emoji": "🔬",
            "difficulty": "Medium",
            "time_est": "25 mins",
            "stem_tag": "Science",
            "tagline": "Squeeze different stuffing materials and measure which springs back most — real materials science!",
            "steps": [
                "Remove a handful of stuffing from an old teddy bear (or use cotton balls, foam, crumpled paper).",
                "Compress each material into a cup and measure its compressed height with a ruler.",
                "Release and immediately measure how high it bounces back.",
                "Calculate the rebound ratio: recovered height ÷ compressed height × 100%.",
                "Rank materials by rebound — which makes the best cushioning and why?",
            ],
            "materials": ["teddy bear", "cup", "ruler", "cotton balls", "foam", "paper"],
            "learn": "You'll learn about elasticity and resilience — how materials store and release energy when compressed.",
        },
    ],

    "scissors": [
        {
            "title": "Lever Mechanical Advantage Lab",
            "emoji": "✂️",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Scissors ARE levers — measure how blade length changes the force you need to cut!",
            "steps": [
                "Cut the same strip of cardboard near the tip of scissors, then at the middle, then near the pivot.",
                "Rate how hard each cut feels on a 1–5 scale and record results.",
                "Measure the distance from the pivot to each cutting point (effort arm and load arm).",
                "Calculate mechanical advantage = effort arm ÷ load arm for each position.",
                "Explain why cutting near the pivot always requires more force.",
            ],
            "materials": ["scissors", "cardboard", "ruler", "paper", "pencil"],
            "learn": "You'll learn about levers — how the distance from a pivot determines the mechanical advantage.",
        },
        {
            "title": "Paper Bridge Stress Test",
            "emoji": "🌉",
            "difficulty": "Hard",
            "time_est": "45 mins",
            "stem_tag": "Engineering",
            "tagline": "Cut and fold paper into structural shapes — then load-test which design holds the most weight!",
            "steps": [
                "Cut 10 equal strips of paper (3 cm × 20 cm) using scissors.",
                "Use strips to build 3 different bridge designs spanning a 15 cm gap: flat, folded arch, triangular truss.",
                "Load each bridge with coins one at a time until it collapses.",
                "Record the maximum load for each design.",
                "Calculate the strength-to-weight ratio: load held ÷ paper mass (estimate 5g per sheet).",
            ],
            "materials": ["scissors", "paper", "coins", "ruler", "tape"],
            "learn": "You'll learn about structural engineering — why triangles and arches resist collapse better than flat shapes.",
        },
    ],

    "toothbrush": [
        {
            "title": "Vibrobot Racer",
            "emoji": "🤖",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "stem_tag": "Engineering",
            "tagline": "Turn a toothbrush into a vibrating robot that walks itself across a table!",
            "steps": [
                "Snap off the handle from an old electric toothbrush head, or use a manual brush.",
                "Tape a small watch battery to the base and attach a small motor (from an old toy) or just use the vibrating element.",
                "For a simpler version: tape a phone set to vibrate on top of the brush bristle side down.",
                "Set it on a flat surface and watch the angled bristles propel it forward.",
                "Race two vibrobots and measure speeds in cm/s over a 30 cm course.",
            ],
            "materials": ["toothbrush", "tape", "battery", "ruler", "stopwatch"],
            "learn": "You'll learn how angled bristles convert vibration energy into directional motion — like a tiny walking machine.",
        },
        {
            "title": "Plaque Acid Experiment",
            "emoji": "🦷",
            "difficulty": "Medium",
            "time_est": "30 mins + 24 hrs",
            "stem_tag": "Science",
            "tagline": "Test whether brushing really removes the bacteria acid that dissolves tooth enamel!",
            "steps": [
                "Place 4 eggshell pieces (eggshell = calcium like tooth enamel) into 4 cups.",
                "Fill cup 1 with water, cup 2 with orange juice, cup 3 with cola, cup 4 with milk.",
                "After 24 hours, remove each shell and scrub two of the four with a toothbrush and toothpaste.",
                "Compare the surface texture of brushed vs. unbrushed shells in each liquid.",
                "Record which liquid caused most damage and whether brushing reduced it.",
            ],
            "materials": ["toothbrush", "eggshells", "orange juice", "cola", "milk", "water", "cups", "toothpaste"],
            "learn": "You'll learn about acid erosion — how acidic liquids dissolve calcium carbonate, the same mineral in teeth.",
        },
    ],

    "apple": [
        {
            "title": "Oxidation Race",
            "emoji": "🍎",
            "difficulty": "Easy",
            "time_est": "20 mins + observe 1 hr",
            "stem_tag": "Science",
            "tagline": "Discover which household liquids slow down apple browning — and why it works!",
            "steps": [
                "Cut an apple into 6 equal slices.",
                "Dip each slice in a different liquid: lemon juice, vinegar, salt water, plain water, milk, and leave one untreated.",
                "Place all slices on a labeled plate and observe every 15 minutes for 1 hour.",
                "Rate browning on a 1–5 scale at each time point and record in a table.",
                "Graph browning score vs. time for each liquid and explain which worked best and why (hint: acidity and vitamin C).",
            ],
            "materials": ["apple", "lemon juice", "vinegar", "salt", "water", "milk", "knife", "paper", "pencil"],
            "learn": "You'll learn about oxidation — how oxygen reacts with enzymes in cut fruit and how antioxidants slow that reaction.",
        },
        {
            "title": "Density and Buoyancy Test",
            "emoji": "🌊",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "stem_tag": "Science",
            "tagline": "Will an apple float? Test different fruits and predict which ones sink — then explain the science!",
            "steps": [
                "Fill a bowl with water.",
                "Before testing each fruit (apple, orange, banana, carrot), predict float or sink and record your prediction.",
                "Place each fruit gently in the water and observe.",
                "Peel the orange and test again — does it sink now? Record and explain why.",
                "Estimate each fruit's density relative to water (>1 sinks, <1 floats).",
            ],
            "materials": ["apple", "orange", "banana", "carrot", "bowl", "water", "paper", "pencil"],
            "learn": "You'll learn about buoyancy and density — an object floats when its average density is less than the liquid it's in.",
        },
    ],

    "banana": [
        {
            "title": "Enzyme Ripeness Experiment",
            "emoji": "🍌",
            "difficulty": "Medium",
            "time_est": "20 mins + 3-day observation",
            "stem_tag": "Science",
            "tagline": "Track a banana ripening over 3 days and discover how enzymes change colour, starch, and sweetness!",
            "steps": [
                "Buy 3 bananas at the same ripeness level. Label them Day 1, Day 2, Day 3.",
                "Each day, mash one banana and test its sweetness by tasting a tiny bit, and record the peel colour on a 1–7 scale.",
                "Dissolve iodine (from a pharmacy) in water and drop it on a banana slice — dark blue = starch, yellow = sugar.",
                "Record the iodine colour each day and chart starch vs. sweetness over time.",
                "Explain what enzyme (amylase) converts starch to sugar as bananas ripen.",
            ],
            "materials": ["banana", "iodine solution", "water", "plate", "paper", "pencil"],
            "learn": "You'll learn about enzyme activity — how amylase breaks down starch into glucose as fruit ripens.",
        },
        {
            "title": "pH Strip Test Kitchen",
            "emoji": "🧪",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Make natural pH indicator from banana peels and test whether your kitchen is acidic or basic!",
            "steps": [
                "Boil banana peel pieces in water for 5 minutes to extract the pigment.",
                "Let the purple liquid cool, then pour into 6 small cups.",
                "Add a small amount of: lemon juice, vinegar, baking soda solution, soap, tap water, and milk to separate cups.",
                "Observe colour change — pink/red = acid, green/yellow = base.",
                "Rank all 6 substances from most acidic to most basic.",
            ],
            "materials": ["banana", "water", "lemon juice", "vinegar", "baking soda", "soap", "milk", "cups"],
            "learn": "You'll learn about pH scale and how plant pigments called anthocyanins change colour in acid vs. base solutions.",
        },
    ],

    "orange": [
        {
            "title": "Vitamin C Titration Test",
            "emoji": "🍊",
            "difficulty": "Hard",
            "time_est": "40 mins",
            "stem_tag": "Science",
            "tagline": "Perform real food chemistry — measure and compare vitamin C content in different juices!",
            "steps": [
                "Dissolve 1/4 tsp of cornstarch in hot water and cool — this is your indicator solution.",
                "Add a few drops of iodine to the cornstarch solution until it turns dark blue.",
                "Squeeze orange juice and add it drop by drop to the iodine mixture using a straw.",
                "Count drops until the blue colour disappears — more drops = more vitamin C.",
                "Repeat with store-bought OJ, apple juice, and water — compare drop counts.",
            ],
            "materials": ["orange", "cornstarch", "iodine", "water", "straw", "cups", "paper", "pencil"],
            "learn": "You'll learn about titration — a technique chemists use to measure the concentration of a substance.",
        },
        {
            "title": "Citrus Battery",
            "emoji": "🔋",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Technology",
            "tagline": "Generate electricity from an orange — test whether citric acid really powers an LED!",
            "steps": [
                "Insert a copper coin and a zinc-coated nail (galvanized) into a fresh orange segment.",
                "Attach wire to each metal and connect to a small LED.",
                "Test whether the LED glows — this is a real galvanic cell!",
                "Connect 3 orange segments in series and measure increased brightness.",
                "Try lemon and grapefruit — record which citrus produces the most voltage (use a cheap multimeter if available).",
            ],
            "materials": ["orange", "copper coin", "galvanized nail", "wire", "LED", "tape"],
            "learn": "You'll learn about electrochemistry — how two different metals in an acidic solution create an electrical potential.",
        },
    ],

    "couch": [
        {
            "title": "Coefficient of Friction Ramp",
            "emoji": "📐",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Math",
            "tagline": "Use sofa cushions as ramp material and calculate the exact friction coefficient of 5 surfaces!",
            "steps": [
                "Prop a cushion at a low angle and place a book on it.",
                "Slowly raise the cushion angle until the book just starts sliding — measure that angle in degrees.",
                "The coefficient of friction μ = tan(angle in radians) — calculate it.",
                "Repeat with 5 different objects on the cushion surface.",
                "Also test the object on 3 other surfaces (floor, cardboard, tablecloth) and compare μ values.",
            ],
            "materials": ["couch", "cushion", "books", "protractor", "ruler", "paper", "pencil"],
            "learn": "You'll learn how to calculate the coefficient of friction using the tangent of the critical angle of sliding.",
        },
        {
            "title": "Seat Cushion Spring Science",
            "emoji": "🌀",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Discover how foam and springs store energy — measure how much your couch compresses under load!",
            "steps": [
                "Hold a ruler vertically against the couch cushion surface before sitting.",
                "Measure and record the cushion height.",
                "Sit down and immediately measure the new compressed height.",
                "Calculate compression amount and compression percentage.",
                "Add more weight (place a bag of books on lap) and measure again — is compression linear with weight?",
            ],
            "materials": ["couch", "ruler", "books", "bag", "paper", "pencil"],
            "learn": "You'll learn about Hooke's Law — how elastic materials compress proportionally to the load applied.",
        },
    ],

    "potted plant": [
        {
            "title": "Phototropism Tower Challenge",
            "emoji": "☀️",
            "difficulty": "Medium",
            "time_est": "15 mins + 5-day observation",
            "stem_tag": "Science",
            "tagline": "Block light from all but one side and watch your plant bend toward the sun — measure its growth angle!",
            "steps": [
                "Cut three sides of a cardboard box so light only enters from one side.",
                "Place the potted plant inside the box with the open side facing a window.",
                "Measure the stem angle (from vertical) on day 1, 3, and 5 using a protractor.",
                "Rotate the box 180° on day 5 so light comes from the opposite side and observe.",
                "Record and graph stem angle vs. day number.",
            ],
            "materials": ["potted plant", "cardboard box", "scissors", "protractor", "ruler", "paper"],
            "learn": "You'll learn about phototropism — how auxin hormone causes plant cells to elongate toward light sources.",
        },
        {
            "title": "Transpiration Rate Experiment",
            "emoji": "💧",
            "difficulty": "Hard",
            "time_est": "30 mins + 24-hr check",
            "stem_tag": "Science",
            "tagline": "Bag a leaf and collect the water it breathes out — measure how much a plant sweats in a day!",
            "steps": [
                "Securely tie a clear zip-lock bag around one leafy branch of the plant.",
                "Set in a sunny window and leave for 24 hours.",
                "Measure water droplets inside the bag by blotting onto paper and weighing (or estimating volume).",
                "Repeat in shade — compare water loss in sun vs. shade.",
                "Calculate approximate transpiration rate: ml of water per hour per leaf.",
            ],
            "materials": ["potted plant", "zip-lock bag", "string", "ruler", "paper", "pencil"],
            "learn": "You'll learn about transpiration — the process by which plants release water vapour through tiny pores called stomata.",
        },
    ],

    "bowl": [
        {
            "title": "Standing Wave Patterns",
            "emoji": "🌊",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "stem_tag": "Science",
            "tagline": "Vibrate a bowl of water with sound and watch standing wave patterns form on the surface!",
            "steps": [
                "Fill a metal or glass bowl with water to about 2 cm depth.",
                "Place near a speaker playing a constant tone (use a tone generator app on your phone).",
                "Slowly increase the frequency until you see the water surface form a regular pattern.",
                "Sprinkle flour or glitter lightly on the surface to make the wave pattern visible.",
                "Record which frequencies create the clearest patterns — these are resonant frequencies of your bowl.",
            ],
            "materials": ["bowl", "water", "flour or glitter", "speaker or phone"],
            "learn": "You'll learn about resonance and standing waves — how objects vibrate at specific natural frequencies.",
        },
        {
            "title": "Archimedes Volume Calculator",
            "emoji": "📐",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Math",
            "tagline": "Calculate the exact volume of weirdly shaped objects using water displacement — Archimedes' method!",
            "steps": [
                "Fill a bowl to the brim with water and place it inside a larger container to catch overflow.",
                "Gently lower 5 irregular objects (rock, apple, toy, key, soap bar) one at a time into the full bowl.",
                "Collect the overflow water in the outer container and measure its volume with a measuring cup.",
                "That overflow volume = the object's volume.",
                "Record and rank the 5 objects by volume from smallest to largest.",
            ],
            "materials": ["bowl", "water", "measuring cup", "rocks", "apple", "soap bar", "key", "paper", "pencil"],
            "learn": "You'll learn about water displacement — how the volume of liquid displaced equals the volume of a submerged object.",
        },
    ],

    "spoon": [
        {
            "title": "Spoon Convex/Concave Mirror Lab",
            "emoji": "🔭",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "stem_tag": "Science",
            "tagline": "A spoon has TWO different mirrors built in — discover how each one flips and distorts your reflection!",
            "steps": [
                "Hold a metal spoon at arm's length and look at the concave side (bowl side) — your image is upside-down!",
                "Slowly bring the spoon toward your face — at what distance does the image flip right-side-up?",
                "Now look at the convex side (back of spoon) — is your image bigger or smaller than life?",
                "Draw ray diagrams for each side showing where light rays converge or diverge.",
                "Measure the approximate focal length by finding where a distant light source focuses on a paper.",
            ],
            "materials": ["spoon", "paper", "pencil", "ruler"],
            "learn": "You'll learn about concave and convex mirrors — how curved surfaces converge and diverge reflected light rays.",
        },
        {
            "title": "Electrostatics Bender",
            "emoji": "⚡",
            "difficulty": "Easy",
            "time_est": "10 mins",
            "stem_tag": "Science",
            "tagline": "Bend a stream of water with a charged spoon — invisible electrostatic forces made visible!",
            "steps": [
                "Turn on a thin stream of water at the tap.",
                "Rub the back of a plastic spoon vigorously on a wool sweater for 20 seconds.",
                "Hold the charged spoon near (not touching) the water stream.",
                "Observe and measure how much the stream bends (estimate in cm).",
                "Try charging a metal spoon the same way — does it work? Explain why or why not.",
            ],
            "materials": ["spoon", "wool fabric", "water", "ruler"],
            "learn": "You'll learn about electrostatic attraction — how static charge on an insulator attracts nearby polar water molecules.",
        },
    ],

    "fork": [
        {
            "title": "Balancing Fork Gravity Trick",
            "emoji": "⚖️",
            "difficulty": "Medium",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Balance two forks and a coin on the tip of a toothpick — defy gravity with center of mass!",
            "steps": [
                "Interlock two forks at their tines so they form a V-shape.",
                "Wedge a coin between the two forks at the base.",
                "Balance the coin's edge on the tip of a toothpick stuck in a cup of playdough.",
                "Once balanced, adjust the fork angles until the system is stable.",
                "Measure the angle between the forks and the distance the coin hangs below the pivot — explain why it balances.",
            ],
            "materials": ["fork", "coin", "toothpick", "cup", "playdough or clay"],
            "learn": "You'll learn about center of mass — a system balances when its combined center of mass is directly below the pivot point.",
        },
        {
            "title": "Surface Tension Measurement",
            "emoji": "💧",
            "difficulty": "Medium",
            "time_est": "25 mins",
            "stem_tag": "Science",
            "tagline": "Float a fork on water and test which liquids destroy surface tension most — quantified!",
            "steps": [
                "Gently lay a fork flat on water surface using a tissue to lower it — it should float!",
                "Add one drop of dish soap near the fork and observe what happens.",
                "Refill the cup and repeat, this time adding: salt, sugar, alcohol, and oil one at a time.",
                "Rate each substance's effect on 1–5 scale (5 = fork sinks immediately).",
                "Rank the substances by how strongly they break surface tension.",
            ],
            "materials": ["fork", "water", "dish soap", "salt", "sugar", "alcohol", "oil", "tissue", "cup"],
            "learn": "You'll learn about surface tension — the cohesive force between water molecules and how surfactants break it.",
        },
    ],

    "vase": [
        {
            "title": "Resonant Frequency Finder",
            "emoji": "🎵",
            "difficulty": "Medium",
            "time_est": "25 mins",
            "stem_tag": "Science",
            "tagline": "Find the exact pitch that makes your vase sing — every container has its own resonant frequency!",
            "steps": [
                "Fill the vase with water to 5 different levels (empty, 1/4, 1/2, 3/4, full).",
                "Blow gently across the opening at each level and listen to the pitch.",
                "Record each pitch using a free piano app on your phone to identify the note.",
                "Measure the air column height above the water at each level.",
                "Plot air column height vs. musical note frequency — find the pattern.",
            ],
            "materials": ["vase", "water", "ruler", "phone with piano app", "paper", "pencil"],
            "learn": "You'll learn about resonance in air columns — why shorter air columns vibrate faster and produce higher pitches.",
        },
        {
            "title": "Capillary Action Dye Race",
            "emoji": "🌺",
            "difficulty": "Easy",
            "time_est": "15 mins + 30 min observation",
            "stem_tag": "Science",
            "tagline": "Place white flowers in coloured water and watch capillary action pull dye up the stem!",
            "steps": [
                "Fill the vase with water and add 10 drops of food coloring.",
                "Place a white flower (or celery stalk) in the coloured water.",
                "Mark the dye level on the stem with a pen every 10 minutes for 30 minutes.",
                "Split the stem partway up and place each half in different coloured water.",
                "After 1 hour, observe the split petals — record which colour appears on which side.",
            ],
            "materials": ["vase", "water", "food coloring", "white flowers or celery", "pen", "ruler"],
            "learn": "You'll learn about capillary action — how adhesion and cohesion forces pull water upward through narrow plant vessels.",
        },
    ],

    "bed": [
        {
            "title": "Sleep Position Pressure Map",
            "emoji": "🛏️",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Science",
            "tagline": "Map where your mattress presses hardest using pressure-sensitive paper — real biomechanics!",
            "steps": [
                "Lay a large sheet of paper on the bed and put a thin layer of flour on top.",
                "Lie down normally for 30 seconds then carefully stand up.",
                "Observe which areas show the most flour compression (these are highest pressure zones).",
                "Measure the area of each major impression with a ruler and estimate pressure (your weight / contact area).",
                "Compare lying on your back vs. side — which distributes pressure more evenly?",
            ],
            "materials": ["bed", "paper", "flour", "ruler", "pencil"],
            "learn": "You'll learn about pressure distribution — how force spread over a larger area reduces pressure on any single point.",
        },
        {
            "title": "Mattress Spring Constant Lab",
            "emoji": "🌀",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Math",
            "tagline": "Measure your mattress's spring constant using Hooke's Law — real physics on your bed!",
            "steps": [
                "Measure the mattress height at an unloaded corner with a ruler.",
                "Place a heavy book on that corner and measure the new compressed height.",
                "Calculate compression in metres and weight of books in Newtons (mass × 9.8).",
                "Spring constant k = Force ÷ Compression (in N/m).",
                "Add more books, take more readings, and check whether k stays constant (Hooke's Law predicts it will).",
            ],
            "materials": ["bed", "books", "ruler", "scale to weigh books", "paper", "pencil"],
            "learn": "You'll learn about Hooke's Law — that elastic materials compress in direct proportion to the force applied.",
        },
    ],

    "tv": [
        {
            "title": "Pixel Colour Mixer",
            "emoji": "🖥️",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "stem_tag": "Technology",
            "tagline": "Zoom into a TV screen and see the red, green, and blue pixels — discover additive colour mixing!",
            "steps": [
                "Display a solid white, red, green, blue, and yellow image on the TV screen (search for 'solid color wallpaper').",
                "Use a magnifying glass (or water-drop lens: tape a water drop on plastic wrap) to zoom into the screen surface.",
                "Sketch or photograph the pixel pattern for each colour.",
                "Try to see which sub-pixels light up for yellow — is it R+G? Confirm with your magnifier.",
                "Research: why do screens use RGB instead of the paint colours red, yellow, blue?",
            ],
            "materials": ["tv", "magnifying glass or plastic wrap", "water", "paper", "pencil"],
            "learn": "You'll learn about additive colour mixing — screens combine red, green, and blue light to create every colour you see.",
        },
        {
            "title": "Screen Refresh Rate Test",
            "emoji": "⚡",
            "difficulty": "Medium",
            "time_est": "25 mins",
            "stem_tag": "Technology",
            "tagline": "Detect your TV's refresh rate using slow-motion video — the invisible flicker made visible!",
            "steps": [
                "Set your phone to slow-motion mode (120fps or 240fps if available).",
                "Display a rapidly flashing white/black alternating image on the TV (search 'strobe test pattern').",
                "Film the TV in slow motion and play back the footage.",
                "Count how many bright flashes appear per second in the slow-motion video.",
                "Calculate actual refresh rate: flashes × (phone fps ÷ playback fps) = Hz.",
            ],
            "materials": ["tv", "cell phone", "paper", "pencil"],
            "learn": "You'll learn about refresh rate — how often a screen redraws its image per second, and why it matters for motion clarity.",
        },
    ],

    "sink": [
        {
            "title": "Water Filter Engineering Challenge",
            "emoji": "💧",
            "difficulty": "Hard",
            "time_est": "45 mins",
            "stem_tag": "Engineering",
            "tagline": "Engineer a water filter from kitchen materials and measure how much sediment it removes!",
            "steps": [
                "Mix muddy water in a cup (soil + tap water).",
                "Cut the bottom off a bottle and layer: cotton ball, sand, gravel, activated charcoal (or crushed charcoal).",
                "Pour the muddy water through and collect the output.",
                "Compare the turbidity (cloudiness) of input vs. output by looking through both cups at a light source.",
                "Redesign the filter with different layer orders and compare which order produces clearest water.",
            ],
            "materials": ["sink", "bottle", "cotton balls", "sand", "gravel", "soil", "water", "cups"],
            "learn": "You'll learn about filtration and water treatment — how different particle sizes are trapped by different filter media.",
        },
        {
            "title": "Soap Surface Tension Lab",
            "emoji": "🫧",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Count how many drops of water fit on a coin and discover what soap does to surface tension!",
            "steps": [
                "Place a clean dry coin flat on the counter near the sink.",
                "Using a straw as a dropper, add water drops one at a time and count until overflow.",
                "Record the number of drops that fit.",
                "Now mix 1 drop of dish soap into the water and repeat the experiment.",
                "Calculate the % reduction in drop count and explain why soap reduces surface tension.",
            ],
            "materials": ["sink", "coin", "water", "dish soap", "straw", "paper", "pencil"],
            "learn": "You'll learn about surface tension and surfactants — how soap molecules disrupt the hydrogen bonds between water molecules.",
        },
    ],

    "refrigerator": [
        {
            "title": "Heat Transfer Insulation Race",
            "emoji": "🌡️",
            "difficulty": "Hard",
            "time_est": "45 mins",
            "stem_tag": "Engineering",
            "tagline": "Engineer the best container to keep ice frozen longest — beat the fridge's head start!",
            "steps": [
                "Place identical ice cubes in 5 cups, each wrapped in a different material: foil, newspaper, fabric, cardboard, nothing.",
                "Set all cups on the counter at the same time and check every 5 minutes.",
                "Record the time until each ice cube fully melts.",
                "Calculate melt rate in grams per minute by estimating the ice mass at start (1 cm³ ≈ 0.9 g).",
                "Compare your best insulator against simply leaving ice in the refrigerator — which wins?",
            ],
            "materials": ["refrigerator", "ice", "cups", "foil", "newspaper", "fabric", "cardboard", "ruler", "clock"],
            "learn": "You'll learn about thermal conductivity — how different materials resist the flow of heat energy.",
        },
        {
            "title": "Cooling Rate Curve",
            "emoji": "📉",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Math",
            "tagline": "Graph how quickly a hot drink cools — discover Newton's Law of Cooling in your kitchen!",
            "steps": [
                "Heat a cup of water in the microwave to about 60°C (hot but not boiling).",
                "Record the temperature every 2 minutes for 20 minutes using a cooking thermometer.",
                "Plot temperature on the y-axis vs. time on the x-axis.",
                "Now place an identical cup in the refrigerator and repeat the measurements.",
                "Compare the two cooling curves — which matches Newton's exponential cooling model better?",
            ],
            "materials": ["refrigerator", "water", "cup", "cooking thermometer", "microwave", "clock", "paper", "pencil"],
            "learn": "You'll learn about Newton's Law of Cooling — objects lose heat proportional to the temperature difference with their surroundings.",
        },
    ],

    "umbrella": [
        {
            "title": "Parachute Drop Science",
            "emoji": "🪂",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Engineering",
            "tagline": "Test whether canopy size really changes fall time — measure drag force with your umbrella!",
            "steps": [
                "Open the umbrella and tie a small bag of coins to the handle as a payload.",
                "Drop from a safe height (stairs or second floor window if accessible) and time the fall.",
                "Close the umbrella and drop the same payload again — time it.",
                "Calculate terminal velocity by dividing fall height by fall time.",
                "Also test a plastic bag parachute and compare all three fall times.",
            ],
            "materials": ["umbrella", "coins", "bag", "stopwatch", "ruler", "plastic bag"],
            "learn": "You'll learn about air resistance and terminal velocity — larger canopy area increases drag, slowing descent.",
        },
        {
            "title": "Wind Speed Anemometer",
            "emoji": "💨",
            "difficulty": "Medium",
            "time_est": "35 mins",
            "stem_tag": "Engineering",
            "tagline": "Build a cup anemometer and calibrate it with a fan — measure real wind speed in your yard!",
            "steps": [
                "Cut 4 small cups and tape them to the ends of two crossed straws, all facing the same rotational direction.",
                "Pin the straw cross through its centre onto the top of an umbrella handle so it can spin freely.",
                "Hold the umbrella in front of a fan set to low, medium, and high — count cup rotations per 10 seconds.",
                "Stand outside and count rotations in 10-second intervals at different times of day.",
                "If you know the fan's speed setting, calibrate: rotations per second → wind speed.",
            ],
            "materials": ["umbrella", "cups", "straws", "tape", "pin", "stopwatch", "paper", "pencil"],
            "learn": "You'll learn about anemometry — how rotation rate relates to wind speed and how instruments are calibrated.",
        },
    ],

    "cake": [
        {
            "title": "Baking Soda CO₂ Inflator",
            "emoji": "🎈",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "stem_tag": "Science",
            "tagline": "Capture the CO₂ released by the same gas that makes cakes rise — and inflate a balloon with it!",
            "steps": [
                "Pour 2 tablespoons of baking soda into an empty bottle.",
                "Pour 4 tablespoons of vinegar into a balloon using a funnel.",
                "Carefully stretch the balloon over the bottle neck without spilling the vinegar yet.",
                "Lift the balloon upright so the vinegar falls into the bottle and triggers the reaction.",
                "Measure the balloon diameter every 30 seconds until inflation stops.",
            ],
            "materials": ["cake", "baking soda", "vinegar", "bottle", "balloon", "funnel", "ruler"],
            "learn": "You'll learn about acid-base reactions that produce CO₂ gas — the same reaction that makes cakes rise in the oven.",
        },
        {
            "title": "Yeast Fermentation Test",
            "emoji": "🧫",
            "difficulty": "Medium",
            "time_est": "30 mins + 1 hr observe",
            "stem_tag": "Science",
            "tagline": "Feed yeast sugar vs. no sugar and measure how much CO₂ each produces — biological baking science!",
            "steps": [
                "Mix yeast with warm water in two cups — add sugar to one, nothing to the other.",
                "Stretch a balloon over each cup opening.",
                "Every 10 minutes for 1 hour, measure how much the balloon has inflated (circumference with string).",
                "Plot balloon size vs. time for both cups on the same graph.",
                "Explain why yeast with sugar inflates the balloon more (hint: fermentation).",
            ],
            "materials": ["cake", "yeast", "sugar", "warm water", "cups", "balloons", "string", "ruler", "clock"],
            "learn": "You'll learn about fermentation — how yeast converts sugar into CO₂ and ethanol through cellular respiration.",
        },
    ],

    "pizza": [
        {
            "title": "Geometry of the Slice",
            "emoji": "📐",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Math",
            "tagline": "Calculate the exact area and crust-to-topping ratio of a pizza slice using circle geometry!",
            "steps": [
                "Measure the diameter of a round pizza (or draw one on paper).",
                "Calculate the full circle's area using A = πr².",
                "Measure the crust width along the outer edge.",
                "Calculate the 'topping zone' area (smaller circle minus crust annulus).",
                "For 8 slices: what is each slice's area? Compare the topping ratio of a normal vs. extra-large slice.",
            ],
            "materials": ["pizza", "ruler", "paper", "pencil", "calculator"],
            "learn": "You'll learn about circle geometry — area formulas, sectors, and the annulus formula for ring-shaped regions.",
        },
        {
            "title": "Grease Stain Absorbency Test",
            "emoji": "🧻",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Test which paper type absorbs the most pizza grease — the science of porosity and absorption!",
            "steps": [
                "Cut equal 10 cm × 10 cm squares of: paper towel, newspaper, cardboard, wax paper, and printer paper.",
                "Drip the same 5 drops of vegetable oil onto each square.",
                "After 5 minutes, hold each square up to a light source and rate translucency 1–5 (5 = most oil absorbed).",
                "Weigh each square before and after to calculate mass of oil absorbed (if a scale is available).",
                "Rank the materials by absorbency and explain what material properties cause the differences.",
            ],
            "materials": ["pizza", "paper towel", "newspaper", "cardboard", "wax paper", "vegetable oil", "ruler"],
            "learn": "You'll learn about porosity and absorption — how the pore structure of a material determines how much liquid it holds.",
        },
    ],

    "donut": [
        {
            "title": "Torus Geometry Explorer",
            "emoji": "🍩",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Math",
            "tagline": "Calculate the volume and surface area of a donut using the mathematics of a torus!",
            "steps": [
                "Measure the donut's outer diameter (R), inner hole diameter, and cross-section radius (r) with a ruler.",
                "Calculate torus volume: V = 2π² × R × r²",
                "Calculate torus surface area: A = 4π² × R × r",
                "Estimate the donut's mass by weighing on a kitchen scale and calculate its density.",
                "Compare: if you reshaped the donut into a sphere of the same volume, what would its radius be?",
            ],
            "materials": ["donut", "ruler", "calculator", "kitchen scale", "paper", "pencil"],
            "learn": "You'll learn about torus geometry — the mathematics that describes donut, tyre, and ring shapes in 3D space.",
        },
        {
            "title": "Sugar Crystallization Lab",
            "emoji": "💎",
            "difficulty": "Hard",
            "time_est": "30 mins + 3-day grow",
            "stem_tag": "Science",
            "tagline": "Grow rock candy crystals and observe how temperature affects crystal size — real chemistry!",
            "steps": [
                "Dissolve as much sugar as possible in hot water (supersaturated solution) — about 2 cups sugar per 1 cup water.",
                "Pour into a clear jar and let cool to room temperature.",
                "Dip a string in the solution and let dry — it becomes a seed crystal nucleation point.",
                "Hang the string in the jar and leave undisturbed for 3 days.",
                "Compare crystals grown at room temperature vs. in the refrigerator — which are bigger and why?",
            ],
            "materials": ["donut", "sugar", "water", "jar", "string", "pencil", "stove or microwave"],
            "learn": "You'll learn about supersaturation and crystallization — how dissolved molecules arrange into ordered crystal lattices.",
        },
    ],

    "sandwich": [
        {
            "title": "Calorie Estimation Challenge",
            "emoji": "🧮",
            "difficulty": "Medium",
            "time_est": "25 mins",
            "stem_tag": "Math",
            "tagline": "Calculate the approximate calories in your sandwich using food labels — nutrition meets math!",
            "steps": [
                "Weigh each sandwich ingredient on a kitchen scale.",
                "Find the calorie density of each ingredient (calories per gram) from its food label.",
                "Calculate: ingredient calories = grams × (calories per 100g ÷ 100).",
                "Sum all ingredients to get total sandwich calories.",
                "Calculate what percentage of a recommended 2000-calorie daily intake your sandwich represents.",
            ],
            "materials": ["sandwich", "kitchen scale", "food labels", "calculator", "paper", "pencil"],
            "learn": "You'll learn how to use proportional reasoning to calculate nutritional content from ingredient labels and mass.",
        },
        {
            "title": "Mold Growth Conditions Experiment",
            "emoji": "🦠",
            "difficulty": "Hard",
            "time_est": "20 mins + 5-day observe",
            "stem_tag": "Science",
            "tagline": "Control mold growth by changing moisture and temperature — discover what microbes need to thrive!",
            "steps": [
                "Cut 4 equal pieces of bread (no mold-inhibitors — homemade or artisan bread works best).",
                "Seal piece 1 dry in a bag, piece 2 slightly moistened, piece 3 moistened and warm, piece 4 moistened and refrigerated.",
                "Label each bag and check every 24 hours for 5 days — record the first signs of mold.",
                "Photograph each sample daily and rate mold coverage 0–100%.",
                "Graph mold % vs. days for each condition and identify which variable matters most.",
            ],
            "materials": ["sandwich", "bread", "zip-lock bags", "water", "ruler", "clock", "paper", "pencil"],
            "learn": "You'll learn about microbial growth conditions — how moisture, warmth, and oxygen availability control mold proliferation.",
        },
    ],

    "carrot": [
        {
            "title": "Osmosis Shrinking Lab",
            "emoji": "🔬",
            "difficulty": "Medium",
            "time_est": "20 mins + 1-hr soak",
            "stem_tag": "Science",
            "tagline": "Soak carrots in salt water and watch osmosis shrink them — real cell membrane science!",
            "steps": [
                "Cut 6 carrot sticks of exactly the same length (10 cm) using a ruler.",
                "Prepare 3 solutions: plain water, slightly salty water, very salty water.",
                "Submerge 2 sticks in each solution for 1 hour.",
                "Remove, blot dry, and measure the new length of each stick.",
                "Calculate % length change for each concentration and plot on a bar graph.",
            ],
            "materials": ["carrot", "salt", "water", "ruler", "knife", "cups", "paper", "pencil"],
            "learn": "You'll learn about osmosis — how water moves across a semi-permeable membrane from low to high solute concentration.",
        },
        {
            "title": "Regrowth Growth Rate Tracker",
            "emoji": "📈",
            "difficulty": "Easy",
            "time_est": "10 mins setup + daily measurements",
            "stem_tag": "Science",
            "tagline": "Regrow a carrot top and track its growth curve — graph the math of plant regeneration!",
            "steps": [
                "Cut the top 3 cm off 3 carrots and place cut-side-down in shallow dishes of water.",
                "Place one in full sun, one in shade, and one in no light.",
                "Measure shoot height every day for 7 days with a ruler.",
                "Plot growth curves for all three conditions on the same graph.",
                "Calculate the average daily growth rate (cm/day) for each light condition.",
            ],
            "materials": ["carrot", "water", "shallow dish", "ruler", "paper", "pencil"],
            "learn": "You'll learn about plant regeneration and photosynthesis — how light availability directly controls growth rate.",
        },
    ],

    "person": [
        {
            "title": "Body Proportion Golden Ratio",
            "emoji": "📏",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Math",
            "tagline": "Measure your body proportions and see if the golden ratio (1.618) shows up in human anatomy!",
            "steps": [
                "Measure total height, and the height of your navel from the floor.",
                "Calculate: total height ÷ navel height — is it close to 1.618?",
                "Measure forearm length and hand length — calculate ratio.",
                "Measure finger segment lengths on one finger and calculate consecutive segment ratios.",
                "Record all ratios in a table and find which body part most closely matches φ = 1.618.",
            ],
            "materials": ["person", "ruler", "tape measure", "paper", "pencil", "calculator"],
            "learn": "You'll learn about the golden ratio φ (phi) — an irrational number that appears repeatedly in natural proportions.",
        },
        {
            "title": "Lung Capacity Spirometer",
            "emoji": "🫁",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Build a water-displacement spirometer and measure your actual lung capacity in millilitres!",
            "steps": [
                "Fill a 2-litre bottle to the brim with water and seal with a balloon stretched over the opening.",
                "Invert it into a bowl of water, keeping the opening submerged, and remove the balloon.",
                "Insert a straw under the rim of the bottle into the air pocket.",
                "Take a full deep breath and exhale completely into the straw.",
                "The water that gets displaced = your lung capacity — mark the level and calculate using bottle volume markings.",
            ],
            "materials": ["person", "2-litre bottle", "bowl", "water", "straw", "marker", "ruler"],
            "learn": "You'll learn about lung capacity and how to measure it using water displacement — the same principle Archimedes used.",
        },
    ],

    "cat": [
        {
            "title": "Reaction Time Comparison: Human vs. Cat",
            "emoji": "⚡",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "stem_tag": "Science",
            "tagline": "Compare your reaction speed to a cat's using a string-dangle test — who reacts faster?",
            "steps": [
                "Measure your own reaction time 10 times using the ruler drop method and calculate your average.",
                "Dangle a piece of string in front of your cat and time how quickly it swipes (use slow-motion video).",
                "Analyse the slow-motion footage: count frames from first movement to contact, divide by fps.",
                "Compare average human reaction time (~200–250 ms) to your cat's measured time.",
                "Research the neuroscience: why are cat reflexes faster and what part of the brain controls reflexes?",
            ],
            "materials": ["cat", "string", "ruler", "cell phone", "stopwatch", "paper", "pencil"],
            "learn": "You'll learn about reflex arcs — how nerve signals travel at measurable speeds, determining reaction time.",
        },
        {
            "title": "Pet Behaviour Ethogram",
            "emoji": "📋",
            "difficulty": "Medium",
            "time_est": "20 mins setup + 3 observation sessions",
            "stem_tag": "Science",
            "tagline": "Build a scientific behaviour chart for your cat and analyse its daily activity pattern like a biologist!",
            "steps": [
                "Create a data table with columns: time, behaviour (sleeping/eating/grooming/playing/exploring), duration.",
                "Observe your cat for 15-minute sessions at morning, afternoon, and evening for 3 days.",
                "Tally the time spent in each behaviour per session.",
                "Calculate what percentage of each session is spent in each behaviour.",
                "Draw a pie chart for each time of day — when is your cat most active?",
            ],
            "materials": ["cat", "paper", "pencil", "clock", "ruler", "coloured pens"],
            "learn": "You'll learn about ethology — the scientific study of animal behaviour using systematic observation and data recording.",
        },
    ],

    "dog": [
        {
            "title": "Dog Hearing Frequency Test",
            "emoji": "🐕",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "stem_tag": "Science",
            "tagline": "Find the highest frequency your dog can hear that you can't — test the limits of animal hearing!",
            "steps": [
                "Use a free tone generator app on your phone to produce tones at different frequencies.",
                "Start at 1000 Hz (both you and dog can hear) and increase by 2000 Hz steps.",
                "Watch for ear movement, head tilt, or attention from your dog as the frequency rises.",
                "Note the frequency where your dog reacts but you can no longer hear the tone.",
                "Record results and compare to published hearing ranges (humans 20-20,000 Hz, dogs up to 65,000 Hz).",
            ],
            "materials": ["dog", "phone with tone generator app", "paper", "pencil"],
            "learn": "You'll learn about the frequency spectrum of hearing — how anatomy of the ear determines the range of detectable sound.",
        },
        {
            "title": "Operant Conditioning Experiment",
            "emoji": "🧠",
            "difficulty": "Hard",
            "time_est": "15 mins/day for 5 days",
            "stem_tag": "Science",
            "tagline": "Teach your dog a new trick in 5 days using data-driven positive reinforcement — real behavioural science!",
            "steps": [
                "Choose one new behaviour to teach (e.g. touch a target, spin in a circle).",
                "Each session: 10 trials — reward immediately when dog performs the desired action.",
                "Record success rate (successes ÷ 10 × 100%) for every session.",
                "Plot success rate vs. session number on a graph.",
                "Identify at which session the dog reached 80% accuracy — that is the learning threshold.",
            ],
            "materials": ["dog", "treats", "paper", "pencil", "clock"],
            "learn": "You'll learn about operant conditioning — how reinforcement schedules shape behaviour and how to measure learning rate.",
        },
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# COMBO_MAP  –  bonus STEM projects when 2+ specific objects are detected together
# ─────────────────────────────────────────────────────────────────────────────

COMBO_MAP: dict[frozenset, dict] = {

    frozenset({"bottle", "balloon"}): {
        "title": "Gas Law Demonstrator",
        "emoji": "🎈",
        "difficulty": "Medium",
        "time_est": "25 mins",
        "stem_tag": "Science",
        "tagline": "COMBO UNLOCK! Prove Charles's Law by heating and cooling a balloon-capped bottle and measuring volume change!",
        "steps": [
            "Stretch a balloon over the mouth of an empty plastic bottle.",
            "Submerge the bottle in a bowl of ice water for 5 minutes — observe the balloon.",
            "Move the bottle to a bowl of warm water — observe the balloon again.",
            "Measure the balloon's circumference in each state and calculate approximate volume.",
            "Calculate the ratio of volumes and compare to the temperature ratio (in Kelvin) to confirm Charles's Law.",
        ],
        "materials": ["bottle", "balloon", "bowl", "ice", "warm water", "string", "ruler"],
        "learn": "You'll learn about Charles's Law — gas volume increases proportionally with absolute temperature.",
    },

    frozenset({"cup", "spoon"}): {
        "title": "Non-Newtonian Fluid Lab",
        "emoji": "🌀",
        "difficulty": "Easy",
        "time_est": "20 mins",
        "stem_tag": "Science",
        "tagline": "COMBO UNLOCK! Mix cornstarch and water to create a fluid that acts solid when hit — defy Newton!",
        "steps": [
            "Mix 1 part water to 1.5–2 parts cornstarch in a cup until it has a thick consistency.",
            "Stir slowly with the spoon — it flows easily.",
            "Stir quickly — it resists like a solid.",
            "Slap the surface hard with your palm — it doesn't splash!",
            "Record the difference in resistance at slow vs. fast speeds and explain in terms of viscosity.",
        ],
        "materials": ["cup", "spoon", "cornstarch", "water"],
        "learn": "You'll learn about non-Newtonian fluids — materials whose viscosity changes under different rates of applied stress.",
    },

    frozenset({"bottle", "cup"}): {
        "title": "Hydraulic Lift Model",
        "emoji": "⚙️",
        "difficulty": "Hard",
        "time_est": "45 mins",
        "stem_tag": "Engineering",
        "tagline": "COMBO UNLOCK! Connect two containers with a tube and demonstrate Pascal's hydraulic principle!",
        "steps": [
            "Connect a large bottle and a small cup with a flexible straw sealed with clay.",
            "Fill both with water so there are no air bubbles.",
            "Press down on the cup plunger — observe force transmitted to the bottle side.",
            "Measure the force applied (use a rubber band scale) vs. force output.",
            "Calculate mechanical advantage: output force ÷ input force = ratio of piston areas.",
        ],
        "materials": ["bottle", "cup", "straw", "clay", "water", "rubber band", "ruler"],
        "learn": "You'll learn about Pascal's principle — pressure applied to a confined fluid is transmitted equally in all directions.",
    },

    frozenset({"apple", "orange"}): {
        "title": "Vitamin C Comparative Titration",
        "emoji": "🧪",
        "difficulty": "Hard",
        "time_est": "40 mins",
        "stem_tag": "Science",
        "tagline": "COMBO UNLOCK! Perform a real titration to compare vitamin C concentration in two fruits — lab chemistry at home!",
        "steps": [
            "Squeeze juice from the apple and orange separately.",
            "Make an iodine indicator solution (dissolve iodine in starch water until dark blue).",
            "Add each juice drop by drop to the indicator, counting drops until the blue disappears.",
            "More drops to decolourise = more vitamin C in that juice.",
            "Calculate which fruit has more vitamin C per millilitre and express as a ratio.",
        ],
        "materials": ["apple", "orange", "iodine", "cornstarch", "water", "cups", "straw"],
        "learn": "You'll learn about titration — measuring concentration by counting how much reactant is needed to neutralise a known indicator.",
    },

    frozenset({"bowl", "spoon"}): {
        "title": "Standing Wave Resonance Mapper",
        "emoji": "🎵",
        "difficulty": "Medium",
        "time_est": "30 mins",
        "stem_tag": "Science",
        "tagline": "COMBO UNLOCK! Tap bowl edges with a spoon at different water levels and map the resonant frequencies!",
        "steps": [
            "Fill a metal or glass bowl to 5 different water levels.",
            "Tap the rim gently with the spoon at each level and listen carefully to the pitch.",
            "Record each pitch using a piano app on your phone to identify the musical note.",
            "Measure the water depth for each level.",
            "Plot pitch frequency vs. water depth and describe the mathematical relationship.",
        ],
        "materials": ["bowl", "spoon", "water", "ruler", "phone with piano app", "paper", "pencil"],
        "learn": "You'll learn about resonance — how the mass and tension of vibrating systems determines their natural frequency.",
    },

    frozenset({"laptop", "book"}): {
        "title": "Comparative Reading Speed Study",
        "emoji": "📊",
        "difficulty": "Medium",
        "time_est": "35 mins",
        "stem_tag": "Science",
        "tagline": "COMBO UNLOCK! Measure and compare your reading speed and comprehension on screen vs. paper — real cognitive science!",
        "steps": [
            "Select the same 500-word passage displayed on screen (laptop) and printed on paper.",
            "Read the screen version and time it; answer 5 comprehension questions.",
            "Rest 10 minutes, then read the paper version and time it; answer the same questions.",
            "Calculate words per minute for each: 500 ÷ time in minutes.",
            "Compare speed AND comprehension score — does faster reading mean worse understanding?",
        ],
        "materials": ["laptop", "book", "printer or pen", "stopwatch", "paper", "pencil"],
        "learn": "You'll learn about cognitive load — how the reading medium affects processing speed and comprehension depth.",
    },

    frozenset({"cell phone", "ruler"}): {
        "title": "Gravity Constant Calculator",
        "emoji": "🍎",
        "difficulty": "Hard",
        "time_est": "30 mins",
        "stem_tag": "Math",
        "tagline": "COMBO UNLOCK! Calculate the gravitational constant to within 5% accuracy using your phone camera and a ruler!",
        "steps": [
            "Tape a ruler vertically to a wall.",
            "Set phone to slow-motion (120fps) and film a coin dropped from the 1-metre mark.",
            "Play back frame by frame and record the position of the coin at each frame.",
            "Plot position vs. time² — the slope = ½g, so g = 2 × slope.",
            "Compare your calculated g to 9.81 m/s² and find your percentage error.",
        ],
        "materials": ["cell phone", "ruler", "coin", "tape", "paper", "pencil", "calculator"],
        "learn": "You'll learn how to experimentally determine a physical constant and calculate percentage error from a theoretical value.",
    },

    frozenset({"scissors", "paper"}): {
        "title": "Möbius Strip Topology Explorer",
        "emoji": "♾️",
        "difficulty": "Easy",
        "time_est": "20 mins",
        "stem_tag": "Math",
        "tagline": "COMBO UNLOCK! Cut and twist paper into a shape with only ONE side — discover the impossible geometry of topology!",
        "steps": [
            "Cut a long strip of paper (3 cm wide × 30 cm long) with scissors.",
            "Give one end a half-twist and tape the ends together — you've made a Möbius strip.",
            "Draw a line down the centre without lifting your pen — you return to the start having covered BOTH sides!",
            "Cut down the centre line with scissors — predict what you'll get, then try it.",
            "Make a strip with a full twist instead and compare the results.",
        ],
        "materials": ["scissors", "paper", "tape", "pen", "ruler"],
        "learn": "You'll learn about topology — the branch of math that studies properties preserved through deformation, like one-sided surfaces.",
    },

    frozenset({"carrot", "salt"}): {
        "title": "Osmosis Quantification Experiment",
        "emoji": "⚗️",
        "difficulty": "Hard",
        "time_est": "30 mins + 1-hr soak",
        "stem_tag": "Science",
        "tagline": "COMBO UNLOCK! Measure the exact mass of water that osmosis moves out of a carrot at different salt concentrations!",
        "steps": [
            "Weigh 5 identical carrot sticks (5g each) before soaking.",
            "Prepare 5 salt solutions: 0%, 2%, 5%, 10%, 20% by mass.",
            "Submerge one carrot stick in each solution for 60 minutes.",
            "Remove, blot dry, and weigh each stick — record mass change.",
            "Plot % salt concentration vs. mass change and identify the isotonic point (where mass doesn't change).",
        ],
        "materials": ["carrot", "salt", "water", "cups", "kitchen scale", "ruler", "paper", "pencil"],
        "learn": "You'll learn how to find a solution's isotonic concentration — the point where osmosis reaches equilibrium.",
    },

    frozenset({"umbrella", "stopwatch"}): {
        "title": "Air Resistance Force Calculator",
        "emoji": "🪂",
        "difficulty": "Hard",
        "time_est": "40 mins",
        "stem_tag": "Math",
        "tagline": "COMBO UNLOCK! Time an umbrella falling at terminal velocity and calculate the drag force acting on it!",
        "steps": [
            "Drop an open umbrella from a fixed height (safely indoors or from a low window with supervision).",
            "Time the fall with a stopwatch over a measured distance.",
            "Calculate terminal velocity: v = distance ÷ time.",
            "Estimate drag force using F_drag = mg (at terminal velocity, drag = gravity force).",
            "Weigh the umbrella and convert to Newtons to confirm: F_drag = mass × 9.8.",
        ],
        "materials": ["umbrella", "stopwatch", "ruler", "kitchen scale", "paper", "pencil", "calculator"],
        "learn": "You'll learn about terminal velocity — when drag force equals gravitational force, acceleration reaches zero.",
    },

    frozenset({"fork", "spoon"}): {
        "title": "Balanced Utensil Center of Mass Demo",
        "emoji": "⚖️",
        "difficulty": "Easy",
        "time_est": "15 mins",
        "stem_tag": "Science",
        "tagline": "COMBO UNLOCK! Balance a fork and spoon on the tip of a toothpick and investigate why the center of mass floats!",
        "steps": [
            "Interlock the tines of the fork and spoon together.",
            "Insert a toothpick between them near the curved bowl of the spoon.",
            "Balance the toothpick's free end on the rim of a cup.",
            "Observe that the entire system balances with the center of mass below the pivot.",
            "Remove the fork — does the spoon alone still balance? Explain the difference.",
        ],
        "materials": ["fork", "spoon", "toothpick", "cup"],
        "learn": "You'll learn about center of mass — a system is stable when its combined center of mass hangs directly below its support point.",
    },

    frozenset({"toothbrush", "baking soda"}): {
        "title": "Acid Erosion Protection Test",
        "emoji": "🔬",
        "difficulty": "Medium",
        "time_est": "25 mins + 24-hr check",
        "stem_tag": "Science",
        "tagline": "COMBO UNLOCK! Test whether baking soda toothpaste neutralises acid better than regular toothpaste on eggshell enamel!",
        "steps": [
            "Soak 4 eggshell pieces in cola for 30 minutes to simulate acid exposure.",
            "Remove shells and treat: piece 1 with baking-soda paste + brushing, piece 2 with regular toothpaste + brushing, piece 3 baking soda no brushing, piece 4 no treatment.",
            "Soak all 4 in cola again for another 30 minutes.",
            "Compare surface texture by rubbing gently — which resisted further erosion?",
            "Explain using chemistry: how does baking soda (NaHCO₃) neutralise acid?",
        ],
        "materials": ["toothbrush", "baking soda", "eggshells", "cola", "cups", "toothpaste"],
        "learn": "You'll learn about acid neutralisation — how bases like sodium bicarbonate chemically react with acids to protect surfaces.",
    },

    frozenset({"clock", "pendulum"}): {
        "title": "Pendulum Period vs. Length Verification",
        "emoji": "⏱️",
        "difficulty": "Medium",
        "time_est": "35 mins",
        "stem_tag": "Math",
        "tagline": "COMBO UNLOCK! Verify the pendulum formula T = 2π√(L/g) by timing 5 different string lengths!",
        "steps": [
            "Make 5 pendulums with string lengths: 10, 20, 30, 40, 50 cm.",
            "Time 10 complete swings for each and divide by 10 to get the period T.",
            "Use the formula to calculate the predicted period for each length.",
            "Plot measured T vs. predicted T on a graph — points should fall on a straight line.",
            "Calculate the percentage error for each and identify any outliers.",
        ],
        "materials": ["clock", "string", "washer", "ruler", "stopwatch", "paper", "pencil", "calculator"],
        "learn": "You'll learn how to verify a physics formula experimentally and calculate systematic and random measurement errors.",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Suggestion engine
# ─────────────────────────────────────────────────────────────────────────────

def get_project_suggestions(
    detected_names: List[str],
    max_results: int = 3,
) -> List[dict]:
    """
    Return up to *max_results* project dicts, combo projects first.

    Scoring rules
    -------------
    1. Combo projects score 1000 when ALL required objects appear in detected_names.
    2. Single-object projects score by count of their materials in detected_names.
    3. Ties broken by insertion order.
    4. Duplicate titles are filtered out.
    """
    detected_set = set(detected_names)
    results: list[dict] = []
    seen_titles: set[str] = set()

    # ── Step 1: Combo projects (highest priority) ──────────────────────────
    for key_set, project in COMBO_MAP.items():
        if key_set <= detected_set:
            p = dict(project)
            p["_score"]    = 1000
            p["_is_combo"] = True
            if p["title"] not in seen_titles:
                results.append(p)
                seen_titles.add(p["title"])

    # ── Step 2: Single-object projects, scored by material overlap ─────────
    for obj_name in detected_names:
        for project in PROJECT_MAP.get(obj_name, []):
            if project["title"] in seen_titles:
                continue
            mat_set = set(project.get("materials", []))
            score   = len(mat_set & detected_set)
            p = dict(project)
            p["_score"]    = score
            p["_is_combo"] = False
            results.append(p)
            seen_titles.add(project["title"])

    # ── Step 3: Sort by score descending, trim to max_results ─────────────
    results.sort(key=lambda x: x["_score"], reverse=True)
    return results[:max_results]
