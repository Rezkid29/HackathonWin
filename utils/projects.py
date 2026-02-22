"""
utils/projects.py
-----------------
Project Ideas Engine — maps COCO-detected objects to kid-friendly DIY craft
and activity suggestions with full step-by-step instructions.

PUBLIC API
----------
  PROJECT_MAP  : dict[str, list[dict]]  — per-class project ideas
  COMBO_MAP    : dict[frozenset, dict]  — bonus projects for 2+ objects together
  get_project_suggestions(detected_names, max_results) -> list[dict]
"""

from __future__ import annotations

from typing import List

# ─────────────────────────────────────────────────────────────────────────────
# PROJECT_MAP  –  maps every PREFERRED_CLASS to 2-3 project dicts
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_MAP: dict[str, list[dict]] = {

    "cup": [
        {
            "title": "Cup Herb Garden",
            "emoji": "🌿",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Turn any old cup into a tiny garden that grows on your windowsill!",
            "steps": [
                "Poke 3 small holes in the bottom for drainage.",
                "Fill halfway with potting soil.",
                "Press 5–6 herb seeds into the soil and cover lightly.",
                "Water gently and place on a sunny windowsill.",
                "Watch sprouts appear in 5–7 days!",
            ],
            "materials": ["cup", "soil", "seeds", "water"],
        },
        {
            "title": "Paper Cup Lantern",
            "emoji": "🏮",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Poke a starry pattern and drop in a tea light for magical nighttime glow!",
            "steps": [
                "Draw a star or moon pattern on the outside of the cup.",
                "Use a pin to poke holes along the drawn lines.",
                "Drop a battery-powered tea light inside.",
                "Hang with a ribbon or set as a tabletop centerpiece.",
            ],
            "materials": ["cup", "pin", "ribbon", "tea light"],
        },
        {
            "title": "Water Xylophone",
            "emoji": "🎵",
            "difficulty": "Easy",
            "time_est": "10 mins",
            "tagline": "Fill cups with different water levels and tap out your own tunes!",
            "steps": [
                "Line up 6–8 identical cups in a row.",
                "Fill each with a different amount of water (least to most).",
                "Add a drop of food coloring to each for rainbow flair.",
                "Tap with a metal spoon to hear the different notes!",
            ],
            "materials": ["cup", "water", "spoon", "food coloring"],
        },
    ],

    "bottle": [
        {
            "title": "Bottle Bird Feeder",
            "emoji": "🐦",
            "difficulty": "Easy",
            "time_est": "25 mins",
            "tagline": "Invite feathered friends to your yard with this upcycled bird feeder!",
            "steps": [
                "Cut two small holes opposite each other near the bottle bottom.",
                "Push a wooden skewer through both holes as a perch.",
                "Cut a larger hole just above each perch hole for seed access.",
                "Fill with birdseed, cap tightly, and hang upside-down from a branch.",
            ],
            "materials": ["bottle", "scissors", "skewer", "birdseed", "string"],
        },
        {
            "title": "Bottle Bowling Alley",
            "emoji": "🎳",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Set up 10 bottles and roll a soft ball — indoor bowling lane, no shoes required!",
            "steps": [
                "Fill 10 bottles with a little water to keep them steady.",
                "Arrange in a triangle pattern like real bowling pins.",
                "Mark a throw line with tape on the floor.",
                "Roll a soft ball and track your scores!",
            ],
            "materials": ["bottle", "water", "tape", "ball"],
        },
        {
            "title": "Tornado in a Bottle",
            "emoji": "🌪️",
            "difficulty": "Medium",
            "time_est": "20 mins",
            "tagline": "Make a spinning water vortex you can hold in your hands — pure science magic!",
            "steps": [
                "Fill a bottle 3/4 full with water and a drop of dish soap.",
                "Add glitter or food coloring for drama.",
                "Tape a second bottle neck-to-neck with the first.",
                "Flip and swirl in a circle — watch the tornado form!",
            ],
            "materials": ["bottle", "water", "tape", "glitter", "dish soap"],
        },
    ],

    "book": [
        {
            "title": "Book Nook Diorama",
            "emoji": "🌇",
            "difficulty": "Medium",
            "time_est": "45 mins",
            "tagline": "Transform a hollowed-out book into a tiny secret world on your shelf!",
            "steps": [
                "Stack pages and trace a rectangle in the middle.",
                "Carefully cut through pages to create a hollow box shape.",
                "Paint the inside and let dry completely.",
                "Add tiny figures, LED lights, and mini scenery.",
                "Close the book — your secret diorama is hidden inside!",
            ],
            "materials": ["book", "scissors", "paint", "LED lights", "figurines"],
        },
        {
            "title": "Corner Bookmark Buddy",
            "emoji": "🔖",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Fold a paper corner-bookmark with a funny face that hugs your pages!",
            "steps": [
                "Cut a 15×15 cm square piece of paper.",
                "Fold diagonally to make a triangle.",
                "Fold the top corner down to the centre fold.",
                "Fold each side corner to meet in the middle.",
                "Draw a fun face and add felt ears — slide onto a page corner!",
            ],
            "materials": ["book", "paper", "scissors", "markers", "felt"],
        },
    ],

    "chair": [
        {
            "title": "Blanket Fort Castle",
            "emoji": "🏰",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Build the ultimate cozy castle with chairs and blankets — add fairy lights!",
            "steps": [
                "Arrange 4 chairs in a square, backs outward.",
                "Drape blankets over the tops and sides.",
                "Use clothespins to hold blankets in place.",
                "Add pillows, fairy lights, and snacks inside.",
                "Declare it your Royal Reading Room!",
            ],
            "materials": ["chair", "blankets", "clothespins", "pillows", "fairy lights"],
        },
        {
            "title": "Chair Laser Maze",
            "emoji": "🏃",
            "difficulty": "Easy",
            "time_est": "10 mins",
            "tagline": "Weave yarn between chair legs as 'laser beams' and dodge your way through!",
            "steps": [
                "Place 4–6 chairs in two rows facing each other.",
                "Weave red yarn or string between the legs at different heights.",
                "Challenge: crawl through without touching the 'lasers'.",
                "Time yourself and challenge family members!",
            ],
            "materials": ["chair", "yarn", "stopwatch"],
        },
    ],

    "laptop": [
        {
            "title": "Stop-Motion Movie",
            "emoji": "🎬",
            "difficulty": "Medium",
            "time_est": "60 mins",
            "tagline": "Bring your toys to life! Shoot a 30-second movie one photo at a time.",
            "steps": [
                "Set your laptop camera to face a flat surface.",
                "Place your characters in the scene.",
                "Move them a tiny bit and take a photo each time.",
                "Import photos into any slideshow or movie app.",
                "Play at 8–12 fps for smooth animation!",
            ],
            "materials": ["laptop", "toys", "clay", "paper backdrop"],
        },
        {
            "title": "Podcast Recording Studio",
            "emoji": "🎙️",
            "difficulty": "Easy",
            "time_est": "30 mins",
            "tagline": "Set up a real podcast about your favourite topic — record your first episode!",
            "steps": [
                "Open a free recording app (Audacity, GarageBand, or Voice Memos).",
                "Stack pillows around the microphone for sound dampening.",
                "Write 5 talking points for your show.",
                "Hit record and do a 5-minute episode.",
                "Save and share with family or friends!",
            ],
            "materials": ["laptop", "microphone", "pillows", "notebook"],
        },
    ],

    "cell phone": [
        {
            "title": "DIY Photo Booth",
            "emoji": "📸",
            "difficulty": "Easy",
            "time_est": "30 mins",
            "tagline": "Build a silly prop-filled photo booth and host a mini photoshoot for friends!",
            "steps": [
                "Cut out a large frame from cardboard and decorate it.",
                "Make silly props: mustaches, hats, speech bubbles on sticks.",
                "Hang a colourful sheet or blanket as the backdrop.",
                "Balance the phone on a stack of books as a tripod.",
                "Strike a pose and snap away!",
            ],
            "materials": ["cell phone", "cardboard", "scissors", "paint", "tape"],
        },
        {
            "title": "Cardboard Phone Stand",
            "emoji": "📱",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Fold a sturdy origami-style phone stand from one piece of cardboard!",
            "steps": [
                "Cut a strip of cardboard 30 cm × 8 cm.",
                "Score and fold into 3 sections to make a Z-shape.",
                "Notch the front edge to cradle the phone at a comfortable angle.",
                "Decorate with markers or washi tape.",
            ],
            "materials": ["cell phone", "cardboard", "scissors", "markers"],
        },
    ],

    "keyboard": [
        {
            "title": "Keycap Mosaic Art",
            "emoji": "🎨",
            "difficulty": "Medium",
            "time_est": "40 mins",
            "tagline": "Pop keys from an old keyboard and glue them into a pixelated mosaic masterpiece!",
            "steps": [
                "Pop keycaps from an old or broken keyboard.",
                "Sketch a simple pixel design on cardboard (letter, animal, etc.).",
                "Arrange keycaps like tiles to fill the design.",
                "Glue each key down with strong craft glue and let dry.",
                "Hang your unique tech art on the wall!",
            ],
            "materials": ["keyboard", "cardboard", "craft glue", "paint"],
        },
        {
            "title": "Typing Speed Tournament",
            "emoji": "⚡",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Host a typing race — see who can type a full paragraph the fastest!",
            "steps": [
                "Open any text editor or a free typing website.",
                "Choose a paragraph from your favourite book.",
                "Each player types the paragraph once, timed.",
                "Record all times and crown the champion.",
                "Practice daily and re-challenge in one week!",
            ],
            "materials": ["keyboard", "laptop", "notebook"],
        },
    ],

    "mouse": [
        {
            "title": "Decorated Mouse Pad",
            "emoji": "🖼️",
            "difficulty": "Easy",
            "time_est": "25 mins",
            "tagline": "Draw your own epic artwork on a plain mouse pad using fabric markers!",
            "steps": [
                "Place a plain mouse pad on your work surface.",
                "Sketch a design lightly in pencil.",
                "Trace over with fabric markers or paint pens.",
                "Add details and let dry for 30 minutes.",
                "Optional: seal with a clear sealant spray for durability.",
            ],
            "materials": ["mouse", "mouse pad", "fabric markers", "pencil"],
        },
        {
            "title": "Cable Critter Sculpture",
            "emoji": "🐍",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Coil and shape old cables into animals or abstract desk sculptures!",
            "steps": [
                "Gather old USB or mouse cables.",
                "Bend and coil them into shapes: snakes, spirals, letters.",
                "Use small binder clips to hold shapes in place.",
                "Mount on cardboard for a wall display piece.",
            ],
            "materials": ["mouse", "cables", "binder clips", "cardboard"],
        },
    ],

    "remote": [
        {
            "title": "Button Mosaic Frame",
            "emoji": "🖼️",
            "difficulty": "Easy",
            "time_est": "30 mins",
            "tagline": "Stick buttons from old remotes onto a picture frame for a colourful mosaic!",
            "steps": [
                "Collect buttons and parts from old remotes.",
                "Get a plain wooden or cardboard picture frame.",
                "Apply craft glue and press buttons onto every surface.",
                "Fill every gap for a true mosaic effect.",
                "Let dry 2 hours, then insert your favourite photo!",
            ],
            "materials": ["remote", "picture frame", "craft glue", "buttons"],
        },
        {
            "title": "Button Scavenger Hunt",
            "emoji": "🗺️",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Use the remote as your 'wand' — write clues that each button unlocks!",
            "steps": [
                "Write a clue for each major button on the remote.",
                "Hide small prizes or treats around the room.",
                "Read each clue aloud when pressing a button.",
                "The final clue leads to the grand prize!",
            ],
            "materials": ["remote", "paper", "pen", "prizes"],
        },
    ],

    "clock": [
        {
            "title": "Paper Plate Sundial",
            "emoji": "☀️",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Build a working sundial and tell time with sunlight — just like ancient explorers!",
            "steps": [
                "Push a pencil through the centre of a paper plate.",
                "Tilt the plate to match your latitude angle (~40° in most of the US).",
                "At noon, mark where the shadow falls as '12'.",
                "Mark one new hour every hour until sunset.",
                "Check your sundial vs. the clock the next day!",
            ],
            "materials": ["clock", "paper plate", "pencil", "marker", "tape"],
        },
        {
            "title": "One-Year Time Capsule",
            "emoji": "📦",
            "difficulty": "Easy",
            "time_est": "30 mins",
            "tagline": "Seal today's memories in a box and open it exactly one year from now!",
            "steps": [
                "Find a shoebox or tin with a lid.",
                "Decorate the outside with today's date and a cool design.",
                "Collect 5–10 items: photos, a drawing, a coin, a note to future-you.",
                "Write 'Open on [date one year from now]' on the lid.",
                "Store somewhere safe and set a phone calendar reminder!",
            ],
            "materials": ["clock", "shoebox", "photos", "paper", "pen"],
        },
    ],

    "backpack": [
        {
            "title": "Pocket Herb Garden",
            "emoji": "🌱",
            "difficulty": "Medium",
            "time_est": "40 mins",
            "tagline": "Repurpose an old backpack into a hanging vertical garden for your wall!",
            "steps": [
                "Fill each pocket of an old backpack with small pots or soil bags.",
                "Plant fast-growing herbs: mint, basil, or chives.",
                "Hang the backpack on a sunny outdoor wall or fence.",
                "Water by pouring into the top pocket — it drains to the rest!",
            ],
            "materials": ["backpack", "soil", "herb seeds", "small pots"],
        },
        {
            "title": "Explorer Mission Kit",
            "emoji": "🧭",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Pack your backpack with everything a junior explorer needs and head outside!",
            "steps": [
                "Draw a hand-drawn 'explorer's map' of your yard or neighbourhood.",
                "Pack: magnifying glass, notebook, pencil, snack, water bottle.",
                "Write 5 nature challenges (find a bug, a red leaf, a smooth rock…).",
                "Head out and complete every mission on the list!",
            ],
            "materials": ["backpack", "notebook", "pencil", "magnifying glass"],
        },
    ],

    "teddy bear": [
        {
            "title": "Teddy Bear Hospital",
            "emoji": "🏥",
            "difficulty": "Easy",
            "time_est": "30 mins",
            "tagline": "Fix up worn stuffed animals — sew loose seams and stuff them back to health!",
            "steps": [
                "Inspect your teddy bear for loose seams or missing stuffing.",
                "Thread a needle with matching thread and sew up any holes.",
                "Add extra stuffing through a small opening if needed.",
                "Sew on new button eyes if the old ones are lost.",
                "Wrap in a bandage and write an official 'patient report'!",
            ],
            "materials": ["teddy bear", "needle", "thread", "buttons", "stuffing"],
        },
        {
            "title": "Sock Puppet Theatre",
            "emoji": "🎭",
            "difficulty": "Easy",
            "time_est": "25 mins",
            "tagline": "Make sock puppets to join your teddy bear — put on a whole puppet show!",
            "steps": [
                "Stretch an old sock over your hand.",
                "Sew or glue button eyes onto the toe section.",
                "Cut felt for hair, ears, and a tongue.",
                "Build a stage from a large cardboard box.",
                "Perform a puppet show starring your teddy bear!",
            ],
            "materials": ["teddy bear", "socks", "buttons", "felt", "glue"],
        },
    ],

    "scissors": [
        {
            "title": "Snowflake Galaxy",
            "emoji": "❄️",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Fold and snip paper into unique snowflakes — no two are ever the same!",
            "steps": [
                "Fold a square piece of paper diagonally into a triangle.",
                "Fold two more times to make a small wedge.",
                "Cut notches, curves, and holes along the edges.",
                "Unfold carefully to reveal your snowflake!",
                "Hang with string for a ceiling galaxy display.",
            ],
            "materials": ["scissors", "paper", "string", "tape"],
        },
        {
            "title": "Magazine Vision Board",
            "emoji": "🌈",
            "difficulty": "Easy",
            "time_est": "35 mins",
            "tagline": "Clip inspiring images and words from magazines into a powerful vision board!",
            "steps": [
                "Gather old magazines and newspapers.",
                "Cut out images and words that inspire you.",
                "Arrange them on a large piece of cardboard.",
                "Glue down when you love the layout.",
                "Hang your vision board where you'll see it every morning!",
            ],
            "materials": ["scissors", "magazines", "cardboard", "glue"],
        },
    ],

    "toothbrush": [
        {
            "title": "Splatter Paint Masterpiece",
            "emoji": "🖌️",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Load a toothbrush with paint and flick it — instant Jackson Pollock vibes!",
            "steps": [
                "Lay a large sheet of paper on the floor.",
                "Dip an old toothbrush in watery paint.",
                "Hold over the paper and run your thumb across the bristles.",
                "Switch colours for a multicolour effect.",
                "Let dry and frame your splatter art masterpiece!",
            ],
            "materials": ["toothbrush", "paint", "paper", "cup", "water"],
        },
        {
            "title": "Mini Cleaning Science Lab",
            "emoji": "🔬",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Scrub coins, rocks, and jewellery with baking soda to make them sparkle!",
            "steps": [
                "Collect coins, small rocks, or old jewellery.",
                "Mix baking soda with a little water to make a paste.",
                "Scrub each item with the toothbrush bristles.",
                "Rinse with water and compare before vs. after.",
                "Record your results in a science notebook!",
            ],
            "materials": ["toothbrush", "baking soda", "water", "coins", "bowl"],
        },
    ],

    "apple": [
        {
            "title": "Apple Stamp Garden Print",
            "emoji": "🍎",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Slice an apple crosswise and dip it in paint — the inside makes a perfect star stamp!",
            "steps": [
                "Cut an apple in half crosswise (not top-to-bottom).",
                "Pat the cut side dry with a paper towel.",
                "Press into a plate of paint to coat the surface.",
                "Stamp onto paper, fabric, or greeting cards.",
                "Add a stem with a paintbrush for a finished look!",
            ],
            "materials": ["apple", "paint", "paper", "knife", "brush"],
        },
        {
            "title": "Apple Baking-Soda Volcano",
            "emoji": "🌋",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Hollow an apple and create a fizzing baking-soda volcano — edible science!",
            "steps": [
                "Core the apple to create a hollow chamber.",
                "Place on a tray to catch the overflow.",
                "Add 2 tbsp baking soda and a drop of red food dye.",
                "Pour in vinegar and watch the eruption!",
            ],
            "materials": ["apple", "baking soda", "vinegar", "food coloring", "tray"],
        },
    ],

    "banana": [
        {
            "title": "Banana Peel Stamp",
            "emoji": "🍌",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Scratch a pattern into a banana peel and use it as a natural rubber stamp!",
            "steps": [
                "Peel a banana and keep the peel.",
                "Use a toothpick to scratch a simple design into the inside.",
                "Press onto an ink pad or paint-covered plate.",
                "Stamp onto paper and let dry.",
            ],
            "materials": ["banana", "toothpick", "ink pad", "paper"],
        },
        {
            "title": "Frozen Banana Nice Cream",
            "emoji": "🍦",
            "difficulty": "Easy",
            "time_est": "10 mins + freeze",
            "tagline": "Blend frozen banana into creamy one-ingredient 'ice cream' — no machine needed!",
            "steps": [
                "Peel and slice 2 ripe bananas.",
                "Freeze on a tray for at least 2 hours.",
                "Blend frozen banana in a food processor until silky smooth.",
                "Add peanut butter, cocoa, or berries for flavour.",
                "Scoop and enjoy immediately!",
            ],
            "materials": ["banana", "blender", "bowl", "spoon"],
        },
    ],

    "orange": [
        {
            "title": "Orange Peel Candle",
            "emoji": "🕯️",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "tagline": "The orange pith acts as a natural wick — make an all-natural citrus candle!",
            "steps": [
                "Cut an orange in half and scoop out all the fruit (eat it!).",
                "The central white pith stem naturally acts as a wick.",
                "Fill the shell with olive oil, just below the tip of the pith.",
                "Light the pith carefully with a match.",
                "Enjoy your all-natural citrus candle for up to 6 hours!",
            ],
            "materials": ["orange", "olive oil", "matches"],
        },
        {
            "title": "Dried Orange Slice Garland",
            "emoji": "🍊",
            "difficulty": "Easy",
            "time_est": "20 mins + oven time",
            "tagline": "Bake orange rounds into translucent, beautiful decorations for any room!",
            "steps": [
                "Slice an orange into 5 mm rounds.",
                "Pat dry and arrange on a baking tray.",
                "Bake at 93°C (200°F) for 2–3 hours until papery.",
                "Let cool completely — they'll be translucent and stiff.",
                "Thread on string with a needle and hang as a garland!",
            ],
            "materials": ["orange", "string", "needle", "oven"],
        },
    ],

    "couch": [
        {
            "title": "The Floor Is Lava — Island Hop",
            "emoji": "🏝️",
            "difficulty": "Easy",
            "time_est": "10 mins",
            "tagline": "The floor is lava! Build an island path with sofa cushions and conquer the room!",
            "steps": [
                "Remove all cushions from the couch.",
                "Arrange them in an island path across the room.",
                "Get from one side to the other without touching the floor.",
                "Add 'power-up' objects to collect on each island.",
                "Race against a timer — record your best!",
            ],
            "materials": ["couch", "cushions", "pillows", "timer"],
        },
        {
            "title": "Living Room Drive-In Theatre",
            "emoji": "🎥",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Turn your couch into a drive-in movie 'car' with a cardboard steering wheel!",
            "steps": [
                "Cut a steering wheel from cardboard and tape to a box frame.",
                "Arrange cushions as the car's interior.",
                "Set up a screen (TV or laptop) in front.",
                "Make popcorn and tear paper 'movie tickets'.",
                "Enjoy your custom at-home drive-in night!",
            ],
            "materials": ["couch", "cardboard", "scissors", "popcorn", "tv"],
        },
    ],

    "potted plant": [
        {
            "title": "Mini Fairy Garden",
            "emoji": "🧚",
            "difficulty": "Medium",
            "time_est": "45 mins",
            "tagline": "Build a tiny magical world for fairies right inside a wide plant pot!",
            "steps": [
                "Choose a wide, shallow pot with drainage holes.",
                "Add a gravel layer, then potting soil on top.",
                "Plant small ground-cover plants like moss or succulents.",
                "Add tiny pebble paths, twig fences, and mini figurines.",
                "Place a tiny mirror as a fairy pond!",
            ],
            "materials": ["potted plant", "gravel", "soil", "moss", "pebbles", "figurines"],
        },
        {
            "title": "Painted Terracotta Gallery",
            "emoji": "🎨",
            "difficulty": "Easy",
            "time_est": "30 mins",
            "tagline": "Transform plain terracotta pots into gallery-worthy art with bright acrylics!",
            "steps": [
                "Clean the pot surface and let dry.",
                "Sketch a geometric or nature design in pencil.",
                "Paint with acrylic paints — bold triangles or stripes are easiest!",
                "Add fine details with a thin brush.",
                "Seal with clear varnish when fully dry.",
            ],
            "materials": ["potted plant", "acrylic paint", "brushes", "varnish"],
        },
    ],

    "bowl": [
        {
            "title": "Paper Mache Keepsake Bowl",
            "emoji": "🥣",
            "difficulty": "Medium",
            "time_est": "60 mins + dry time",
            "tagline": "Use a real bowl as a mold to create your own beautiful paper mache bowl!",
            "steps": [
                "Cover the outside of a bowl with plastic wrap.",
                "Mix equal parts white glue and water for paste.",
                "Tear newspaper into strips and dip in paste.",
                "Layer strips over the bowl — 3–4 layers total.",
                "Dry overnight, remove, and paint your creation!",
            ],
            "materials": ["bowl", "newspaper", "white glue", "water", "paint"],
        },
        {
            "title": "Nature Treasure Display",
            "emoji": "🌿",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Go on a nature walk and arrange your finds into a gorgeous display bowl!",
            "steps": [
                "Take a bowl outside on a nature walk.",
                "Collect smooth rocks, interesting seeds, leaves, and sticks.",
                "Arrange your collection by colour or size.",
                "Add a tiny label card naming each treasure.",
                "Display as a centrepiece on your table!",
            ],
            "materials": ["bowl", "rocks", "leaves", "seeds"],
        },
    ],

    "spoon": [
        {
            "title": "Spoon Puppet Family",
            "emoji": "👨‍👩‍👧‍👦",
            "difficulty": "Easy",
            "time_est": "25 mins",
            "tagline": "Paint faces on wooden spoons and create a whole cast of puppet characters!",
            "steps": [
                "Paint the bowl of each wooden spoon a skin tone.",
                "Draw facial features with marker when dry.",
                "Glue on yarn hair, felt clothes, and accessories.",
                "Build a stage from a shoebox cutout.",
                "Put on a spoon puppet show!",
            ],
            "materials": ["spoon", "paint", "markers", "yarn", "felt", "glue"],
        },
        {
            "title": "Kitchen Spoon Wind Chime",
            "emoji": "🎐",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Hang spoons from a stick at different lengths for a tinkling wind chime!",
            "steps": [
                "Find a sturdy stick or wooden dowel.",
                "Tie string to 5–7 metal spoons at different lengths.",
                "Attach strings to the stick, spaced evenly.",
                "Add colourful beads between each spoon.",
                "Hang outside and listen to the music!",
            ],
            "materials": ["spoon", "string", "stick", "beads"],
        },
    ],

    "fork": [
        {
            "title": "Fork Print Flower Garden",
            "emoji": "🌸",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Press a fork in paint and stamp it — the tines make perfect flower petals!",
            "steps": [
                "Dip fork tines into paint on a plate.",
                "Press onto paper in a fan shape to make petals.",
                "Repeat in a circle to complete each flower bloom.",
                "Add stems and leaves with a small brush.",
                "Create a full garden scene on a large sheet!",
            ],
            "materials": ["fork", "paint", "paper", "brush"],
        },
        {
            "title": "Spaghetti Tower Challenge",
            "emoji": "🏛️",
            "difficulty": "Medium",
            "time_est": "40 mins",
            "tagline": "Use dry spaghetti and mini marshmallows to build the tallest tower you can!",
            "steps": [
                "Open a bag of dry spaghetti and mini marshmallows.",
                "Connect spaghetti strands using marshmallows as joints.",
                "Build upward — use triangles for maximum stability.",
                "See how tall you can go before it tips!",
                "Challenge friends to beat your height record.",
            ],
            "materials": ["fork", "spaghetti", "marshmallows"],
        },
    ],

    "vase": [
        {
            "title": "Paper Flower Bouquet",
            "emoji": "💐",
            "difficulty": "Medium",
            "time_est": "40 mins",
            "tagline": "Craft gorgeous paper flowers that last forever — perfect for your vase!",
            "steps": [
                "Cut 6 petal shapes from tissue paper per flower.",
                "Stack all petals and pinch the centre together.",
                "Twist a pipe cleaner around the pinched centre as a stem.",
                "Gently pull each layer upward to open the petals.",
                "Arrange a rainbow bouquet in the vase!",
            ],
            "materials": ["vase", "tissue paper", "scissors", "pipe cleaners"],
        },
        {
            "title": "Decoupage Vase",
            "emoji": "🏺",
            "difficulty": "Medium",
            "time_est": "45 mins",
            "tagline": "Cover a plain vase with torn magazine pages for a colourful patchwork look!",
            "steps": [
                "Tear colourful magazine pages into irregular strips.",
                "Brush Mod Podge (or diluted PVA glue) onto a section of the vase.",
                "Layer paper strips, overlapping slightly.",
                "Apply a coat of Mod Podge over the top to seal.",
                "Continue until the vase is fully covered, then add a final seal coat.",
            ],
            "materials": ["vase", "magazines", "scissors", "Mod Podge", "brush"],
        },
    ],

    "bed": [
        {
            "title": "Epic Pillow Fort Kingdom",
            "emoji": "🏰",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Build the most epic pillow fort your bedroom has ever seen — with a door and windows!",
            "steps": [
                "Pile pillows to form thick walls around your bed.",
                "Drape a large sheet over the bed as the roof.",
                "Use heavy books or shoes to weigh down the sheet edges.",
                "Add a flashlight for interior lighting.",
                "Write the official rules of your kingdom!",
            ],
            "materials": ["bed", "pillows", "blankets", "flashlight", "books"],
        },
        {
            "title": "Indoor Camping Adventure",
            "emoji": "⛺",
            "difficulty": "Easy",
            "time_est": "30 mins",
            "tagline": "Camp in your bedroom — fairy-light stars, sleeping bags, and ghost stories!",
            "steps": [
                "String fairy lights across the ceiling for a starry effect.",
                "Lay sleeping bags on the floor beside the bed.",
                "Make a 'campfire' from paper towel rolls and orange tissue paper.",
                "Make microwave s'mores (marshmallow + chocolate + graham cracker).",
                "Tell ghost stories by flashlight until bedtime!",
            ],
            "materials": ["bed", "fairy lights", "sleeping bag", "flashlight"],
        },
    ],

    "tv": [
        {
            "title": "Cardboard TV Studio",
            "emoji": "📺",
            "difficulty": "Medium",
            "time_est": "45 mins",
            "tagline": "Build a cardboard TV set and record your own talk show, game show, or news broadcast!",
            "steps": [
                "Cut a rectangle window in a large cardboard box.",
                "Decorate the frame with silver paint and craft buttons.",
                "Set up a phone or laptop to record in front of the 'set'.",
                "Write a show script and name your channel.",
                "Film your very first episode!",
            ],
            "materials": ["tv", "cardboard", "scissors", "silver paint", "cell phone"],
        },
        {
            "title": "Digital Art Slideshow Gallery",
            "emoji": "🖼️",
            "difficulty": "Easy",
            "time_est": "30 mins",
            "tagline": "Create a looping art gallery slideshow to display on your TV — impress every visitor!",
            "steps": [
                "Draw or paint 5–10 artworks on paper.",
                "Photograph each piece with a phone.",
                "Create a slideshow in any photo app.",
                "Connect phone or laptop to TV and play on loop.",
                "Host an opening night gallery event for family!",
            ],
            "materials": ["tv", "cell phone", "paper", "paint"],
        },
    ],

    "sink": [
        {
            "title": "Soap Bar Carving",
            "emoji": "🧼",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "tagline": "Carve a bar of soap into an animal or geometric shape — ancient art, modern twist!",
            "steps": [
                "Get a bar of soft soap (Ivory brand works great).",
                "Draw your design outline with a toothpick.",
                "Use a plastic knife to shave away the edges.",
                "Carve details with a toothpick or pen tip.",
                "Smooth the final surface under a gentle trickle of water!",
            ],
            "materials": ["sink", "soap", "toothpick", "plastic knife"],
        },
        {
            "title": "Colour-Mixing Water Lab",
            "emoji": "🔬",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Mix food colouring in cups of water to discover every colour in the rainbow!",
            "steps": [
                "Fill 6 clear cups with water.",
                "Add primary colours (red, yellow, blue) to alternate cups.",
                "Mix neighbouring cups together to make secondary colours.",
                "Record your colour discoveries in a notebook.",
                "Try making the darkest and lightest shade possible!",
            ],
            "materials": ["sink", "cup", "food coloring", "water", "notebook"],
        },
    ],

    "refrigerator": [
        {
            "title": "Custom Fridge Magnets",
            "emoji": "🧲",
            "difficulty": "Easy",
            "time_est": "30 mins",
            "tagline": "Sculpt personalized fridge magnets from air-dry clay and decorate your fridge!",
            "steps": [
                "Cut small shapes from air-dry clay.",
                "Sculpt or stamp patterns into the surface.",
                "Let dry completely (or bake per clay package instructions).",
                "Paint with acrylic colours.",
                "Glue a magnet strip to the back of each piece!",
            ],
            "materials": ["refrigerator", "air-dry clay", "paint", "magnets", "glue"],
        },
        {
            "title": "Leftover Chef Challenge",
            "emoji": "👨‍🍳",
            "difficulty": "Medium",
            "time_est": "30 mins",
            "tagline": "Open the fridge, pick 5 random ingredients, and invent a brand-new recipe!",
            "steps": [
                "List 5 random ingredients you find in the fridge.",
                "Research if they can be safely combined.",
                "Create a dish using only those ingredients.",
                "Plate it beautifully and take a photo.",
                "Rate your creation out of 10 and write the recipe down!",
            ],
            "materials": ["refrigerator", "bowl", "spoon", "fork"],
        },
    ],

    "umbrella": [
        {
            "title": "Umbrella Wind Spinner",
            "emoji": "🌀",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Hang an old umbrella upside-down with streaming ribbons — hypnotic in the wind!",
            "steps": [
                "Open an old umbrella and invert it upside-down.",
                "Tie long, colourful ribbons to each spoke.",
                "Attach string to the handle tip for hanging.",
                "Hang from a tree branch or porch hook outside.",
                "Watch the ribbons spiral in the breeze!",
            ],
            "materials": ["umbrella", "ribbons", "string", "scissors"],
        },
        {
            "title": "Jellyfish Ceiling Decoration",
            "emoji": "🪼",
            "difficulty": "Easy",
            "time_est": "25 mins",
            "tagline": "Turn a small umbrella into an adorable hanging jellyfish for your room!",
            "steps": [
                "Use a small, plain umbrella as the jellyfish bell.",
                "Cut long strips of cellophane or tissue paper.",
                "Tape strips around the umbrella edge as tentacles.",
                "Add googly eyes to the outside dome.",
                "Hang from the ceiling with clear fishing line!",
            ],
            "materials": ["umbrella", "tissue paper", "scissors", "tape", "googly eyes"],
        },
    ],

    "cake": [
        {
            "title": "No-Bake Energy Balls",
            "emoji": "⚡",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Mix oats, honey, and chocolate chips into bite-sized energy balls — snack smarter!",
            "steps": [
                "Mix 1 cup oats, 1/2 cup peanut butter, 1/3 cup honey in a bowl.",
                "Add chocolate chips, chia seeds, or shredded coconut.",
                "Refrigerate the mix for 30 minutes until firm.",
                "Roll into 2 cm balls with clean hands.",
                "Store in the fridge for up to one week!",
            ],
            "materials": ["cake", "oats", "peanut butter", "honey", "chocolate chips", "bowl"],
        },
        {
            "title": "Cupcake Decorating Studio",
            "emoji": "🧁",
            "difficulty": "Medium",
            "time_est": "45 mins",
            "tagline": "Bake plain cupcakes and go wild decorating them as characters, landscapes, or emojis!",
            "steps": [
                "Bake plain cupcakes (or use store-bought ones).",
                "Let cool completely before decorating.",
                "Tint frosting with food colouring for different hues.",
                "Use candy, sprinkles, and piped frosting to create designs.",
                "Photograph before eating — these are too good to miss!",
            ],
            "materials": ["cake", "frosting", "food coloring", "sprinkles", "bowl"],
        },
    ],

    "pizza": [
        {
            "title": "Pizza Box Picture Frame",
            "emoji": "🖼️",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Upcycle a clean pizza box into a rustic picture frame for your favourite photo!",
            "steps": [
                "Flatten a clean, grease-free pizza box.",
                "Cut a window opening in the lid.",
                "Paint or decoupage the outside with cool patterns.",
                "Glue a cardboard backing to hold your photo.",
                "Attach small magnets or a kickstand to display it!",
            ],
            "materials": ["pizza", "cardboard", "scissors", "paint", "photo", "glue"],
        },
        {
            "title": "English Muffin Mini Pizzas",
            "emoji": "🍕",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Make mini pizzas on English muffins — every person designs their own topping combo!",
            "steps": [
                "Split English muffins in half.",
                "Spread tomato sauce on each half.",
                "Add cheese and your favourite toppings.",
                "Bake at 200°C (390°F) for 10 minutes.",
                "Cool for 2 minutes — then enjoy!",
            ],
            "materials": ["pizza", "English muffins", "tomato sauce", "cheese", "toppings"],
        },
    ],

    "donut": [
        {
            "title": "Ring Toss Carnival Game",
            "emoji": "🎯",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Build a donut-inspired ring toss game from cardboard — carnival at home!",
            "steps": [
                "Cut large rings from cardboard (donut-shaped).",
                "Push 5–7 sticks upright into a cardboard base.",
                "Decorate rings with paint or markers.",
                "Assign point values to each stick.",
                "Take turns tossing rings from 2 metres away!",
            ],
            "materials": ["donut", "cardboard", "scissors", "paint", "sticks"],
        },
        {
            "title": "Donut Stamp Wrapping Paper",
            "emoji": "🎁",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Stamp donut patterns on plain paper for the most delicious gift wrap ever!",
            "steps": [
                "Cut a donut shape from a sponge (circle with hole in the middle).",
                "Dip in pink or chocolate-brown paint.",
                "Stamp onto brown kraft paper in repeating rows.",
                "Add sprinkle dots with the eraser end of a pencil.",
                "Wrap a gift — everyone will love the packaging!",
            ],
            "materials": ["donut", "sponge", "paint", "brown paper", "pencil"],
        },
    ],

    "sandwich": [
        {
            "title": "Edible Art Platter",
            "emoji": "🥪",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Arrange sandwich ingredients into edible art — animals, faces, and landscapes!",
            "steps": [
                "Lay bread slices on a plate as your canvas.",
                "Arrange veggie and protein toppings into an animal face.",
                "Use olives for eyes, cucumber for ears, carrot for a mouth.",
                "Photograph your edible masterpiece before eating.",
                "Then enjoy your artful lunch!",
            ],
            "materials": ["sandwich", "vegetables", "carrot", "olives", "knife"],
        },
        {
            "title": "Illustrated Recipe Card",
            "emoji": "📝",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Write and illustrate your own recipe card for the world's greatest sandwich!",
            "steps": [
                "Invent the ideal sandwich with your dream ingredients.",
                "Write the ingredient list with amounts.",
                "Draw step-by-step assembly illustrations.",
                "Decorate the card with food doodles.",
                "Laminate or slip into a plastic sleeve to keep forever!",
            ],
            "materials": ["sandwich", "paper", "markers", "ruler"],
        },
    ],

    "carrot": [
        {
            "title": "Carrot Stamp Butterfly Prints",
            "emoji": "🦋",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Slice a carrot crosswise for oval stamps — arrange four into a butterfly!",
            "steps": [
                "Cut a carrot into rounds of different sizes.",
                "Press each round into paint on a plate.",
                "Stamp 4 ovals in a butterfly wing arrangement.",
                "Add a twig or crayon line as the body and antennae.",
                "Make a whole garden scene with many butterflies!",
            ],
            "materials": ["carrot", "paint", "paper", "brush"],
        },
        {
            "title": "Carrot Top Regrowth Garden",
            "emoji": "🌿",
            "difficulty": "Easy",
            "time_est": "10 mins",
            "tagline": "Regrow carrot tops in water — watch green shoots sprout from kitchen scraps!",
            "steps": [
                "Cut the top 2 cm off a carrot (keep any green if present).",
                "Place cut-side-down in a shallow dish of water.",
                "Set on a sunny windowsill.",
                "Change the water every 2 days.",
                "Watch green shoots appear in just 3–5 days!",
            ],
            "materials": ["carrot", "bowl", "water"],
        },
    ],

    # Extra COCO classes worth covering
    "person": [
        {
            "title": "Shadow Puppet Theatre",
            "emoji": "🎭",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Use your hands and a flashlight to create dramatic shadow puppets on the wall!",
            "steps": [
                "Set a flashlight on a table pointing at a blank white wall.",
                "Dim the room lights.",
                "Practice hand shapes: rabbit, bird, crocodile, wolf.",
                "Create a story with your shadow characters.",
                "Film it as a shadow puppet film!",
            ],
            "materials": ["person", "flashlight", "blank wall"],
        },
        {
            "title": "Life-Size Body Tracing",
            "emoji": "🦸",
            "difficulty": "Easy",
            "time_est": "30 mins",
            "tagline": "Trace your full body on butcher paper and fill it in as your superhero alter ego!",
            "steps": [
                "Tape a long roll of butcher paper to the floor.",
                "Lie down in your favourite heroic pose.",
                "Have a friend trace your outline carefully.",
                "Cut out and decorate as a superhero, alien, or robot!",
                "Hang your life-size portrait on the wall.",
            ],
            "materials": ["person", "butcher paper", "markers", "scissors", "tape"],
        },
    ],

    "cat": [
        {
            "title": "DIY Cat Toy Wand",
            "emoji": "🐱",
            "difficulty": "Easy",
            "time_est": "15 mins",
            "tagline": "Make an irresistible cat wand — your cat will leap and pounce like crazy!",
            "steps": [
                "Find a stick or chopstick as the wand handle.",
                "Tie a 60 cm length of string to one end.",
                "Attach feathers, a crinkle ball, or felt to the string end.",
                "Wave it for your cat and watch them soar!",
            ],
            "materials": ["cat", "stick", "string", "feathers", "felt"],
        },
        {
            "title": "Royal Cat Portrait",
            "emoji": "🎨",
            "difficulty": "Medium",
            "time_est": "40 mins",
            "tagline": "Paint a royal portrait of your cat — complete with a golden crown and velvet background!",
            "steps": [
                "Observe your cat and sketch its basic shape on canvas.",
                "Paint a rich dark background and let dry.",
                "Fill in your cat's fur with layered brushstrokes.",
                "Add a crown, robe, or royal sash.",
                "Write your cat's official royal title along the bottom!",
            ],
            "materials": ["cat", "canvas", "paint", "brushes", "pencil"],
        },
    ],

    "dog": [
        {
            "title": "Homemade Dog Treat Bakery",
            "emoji": "🐕",
            "difficulty": "Easy",
            "time_est": "30 mins",
            "tagline": "Bake peanut-butter dog treats — your pup will be your all-time biggest fan!",
            "steps": [
                "Mix 2 cups flour, 1 cup oats, 2/3 cup peanut butter, 1/2 cup water.",
                "Roll out to 1 cm thickness on a floured surface.",
                "Cut with bone-shaped cookie cutters.",
                "Bake at 180°C (350°F) for 20–25 minutes.",
                "Cool completely before giving treats to your dog!",
            ],
            "materials": ["dog", "flour", "oats", "peanut butter", "water", "bowl"],
        },
        {
            "title": "Backyard Agility Course",
            "emoji": "🏆",
            "difficulty": "Easy",
            "time_est": "20 mins",
            "tagline": "Build a dog agility course from household items and train your pup!",
            "steps": [
                "Set up weave poles using garden stakes or sticks.",
                "Lay a hula hoop flat on the ground as a jump target.",
                "Create a tunnel from a large cardboard box.",
                "Place a plank as a balance beam.",
                "Guide your dog through with treats — time each run!",
            ],
            "materials": ["dog", "cardboard", "sticks", "hula hoop", "treats"],
        },
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# COMBO_MAP  –  bonus projects when 2+ specific objects are detected together
# Keys are frozensets of COCO class names.
# ─────────────────────────────────────────────────────────────────────────────

COMBO_MAP: dict[frozenset, dict] = {

    frozenset({"bottle", "scissors"}): {
        "title": "Bottle Wind Spinner",
        "emoji": "🌀",
        "difficulty": "Medium",
        "time_est": "30 mins",
        "tagline": "COMBO UNLOCK! Cut a bottle into a spiral strip and hang it to spin mesmerizingly in the wind!",
        "steps": [
            "Remove the bottle cap and cut off the bottom.",
            "Cut a continuous spiral strip from bottom to top — like peeling an apple.",
            "Straighten the strip gently and let it curl naturally.",
            "Thread string through the cap hole and hang outdoors.",
            "Watch it spin in the breeze!",
        ],
        "materials": ["bottle", "scissors", "string"],
    },

    frozenset({"cup", "spoon"}): {
        "title": "Kitchen Percussion Band",
        "emoji": "🥁",
        "difficulty": "Easy",
        "time_est": "10 mins",
        "tagline": "COMBO UNLOCK! Tap cups and bowls with spoons to build a full percussion rhythm section!",
        "steps": [
            "Collect cups of different sizes (plastic, metal, ceramic).",
            "Flip them upside-down or leave them right-side-up.",
            "Each surface makes a different pitch when tapped with a spoon.",
            "Create a repeating 4-beat rhythm pattern.",
            "Layer in bowls and bottles for more sounds!",
        ],
        "materials": ["cup", "spoon", "bowl", "bottle"],
    },

    frozenset({"book", "scissors"}): {
        "title": "Book Page Fan Sculpture",
        "emoji": "📖",
        "difficulty": "Medium",
        "time_est": "40 mins",
        "tagline": "COMBO UNLOCK! Fold and trim every page into a 3D fan sculpture — no glue needed!",
        "steps": [
            "Open an old book to the very centre.",
            "Fold each page diagonally toward the spine.",
            "Trim the folded corner for a V-shape cutout if desired.",
            "Continue folding every single page uniformly.",
            "Stand the book up — it holds its own 3D shape!",
        ],
        "materials": ["book", "scissors", "ruler"],
    },

    frozenset({"banana", "apple"}): {
        "title": "Fruit Face Sculpture",
        "emoji": "🍎",
        "difficulty": "Easy",
        "time_est": "15 mins",
        "tagline": "COMBO UNLOCK! Carve and arrange fruit into hilarious edible face sculptures!",
        "steps": [
            "Peel a banana halfway and bend it into a smile shape.",
            "Slice apple rounds as ears and eyebrows.",
            "Use blueberries or grapes for eyes.",
            "Arrange everything on a plate as a funny face.",
            "Photograph, then eat your masterpiece!",
        ],
        "materials": ["banana", "apple", "knife", "plate", "grapes"],
    },

    frozenset({"bowl", "spoon"}): {
        "title": "No-Bake Crunch Bars",
        "emoji": "🍫",
        "difficulty": "Easy",
        "time_est": "20 mins + chill",
        "tagline": "COMBO UNLOCK! Mix, press with a spoon, chill, and cut into perfect crunchy bars!",
        "steps": [
            "Mix 2 cups rice cereal, 1/2 cup honey, 1/2 cup peanut butter in the bowl.",
            "Add chocolate chips or dried fruit and stir with the spoon.",
            "Press firmly into a lined tray using the back of the spoon.",
            "Refrigerate for 1 hour until firm.",
            "Cut into bars and enjoy — or share!",
        ],
        "materials": ["bowl", "spoon", "rice cereal", "honey", "peanut butter"],
    },

    frozenset({"vase", "scissors"}): {
        "title": "Paper Flower Shop",
        "emoji": "🌹",
        "difficulty": "Medium",
        "time_est": "35 mins",
        "tagline": "COMBO UNLOCK! Cut tissue paper into blooms and arrange a forever bouquet in the vase!",
        "steps": [
            "Stack 6 squares of tissue paper per flower.",
            "Accordion-fold the entire stack tightly.",
            "Twist a pipe cleaner around the centre fold as a stem.",
            "Gently pull each layer upward to open the petals.",
            "Arrange a rainbow bouquet in the vase!",
        ],
        "materials": ["vase", "scissors", "tissue paper", "pipe cleaners"],
    },

    frozenset({"laptop", "book"}): {
        "title": "Digital Comic Book",
        "emoji": "💥",
        "difficulty": "Hard",
        "time_est": "90 mins",
        "tagline": "COMBO UNLOCK! Draw comics, photograph them with your laptop, and publish a digital book!",
        "steps": [
            "Sketch a 6-panel comic story on paper.",
            "Ink the pencil lines with a black marker.",
            "Photograph each page with the laptop webcam or camera.",
            "Import into a slideshow to assemble pages.",
            "Add digital speech bubbles and share with friends!",
        ],
        "materials": ["laptop", "book", "markers", "pencil", "paper"],
    },

    frozenset({"cell phone", "book"}): {
        "title": "Audiobook Recording Studio",
        "emoji": "🎙️",
        "difficulty": "Easy",
        "time_est": "30 mins",
        "tagline": "COMBO UNLOCK! Read your favourite chapter aloud and record it as a proper audiobook!",
        "steps": [
            "Choose a chapter from your favourite book.",
            "Set your phone to voice recorder mode.",
            "Surround yourself with blankets for soundproofing.",
            "Read expressively — do different voices for each character!",
            "Save and share with friends who haven't read it yet.",
        ],
        "materials": ["cell phone", "book", "blankets"],
    },

    frozenset({"toothbrush", "cup"}): {
        "title": "Splatter Galaxy Art",
        "emoji": "🌌",
        "difficulty": "Easy",
        "time_est": "20 mins",
        "tagline": "COMBO UNLOCK! Flick dark paint from a toothbrush over cup-mixed colours for a galaxy explosion!",
        "steps": [
            "Paint your paper black and let dry.",
            "Mix white, blue, and purple paint in separate cups.",
            "Hold toothbrush over paper, bristles facing down.",
            "Run your thumb across the bristles to splatter each colour.",
            "Add large star dots with a cotton swab for a finishing touch!",
        ],
        "materials": ["toothbrush", "cup", "paint", "paper"],
    },

    frozenset({"fork", "spoon"}): {
        "title": "Utensil Wind Chime",
        "emoji": "🎐",
        "difficulty": "Easy",
        "time_est": "25 mins",
        "tagline": "COMBO UNLOCK! Hang forks and spoons from a stick for a musical outdoor wind chime!",
        "steps": [
            "Find a sturdy branch or wooden dowel.",
            "Tie string to 6–8 metal forks and spoons at varying lengths.",
            "Alternate them: fork, spoon, fork, spoon.",
            "Space evenly along the dowel and knot tightly.",
            "Hang outside where the breeze will make them chime!",
        ],
        "materials": ["fork", "spoon", "string", "stick"],
    },

    frozenset({"bottle", "cup"}): {
        "title": "Water Xylophone Orchestra",
        "emoji": "🎼",
        "difficulty": "Easy",
        "time_est": "15 mins",
        "tagline": "COMBO UNLOCK! Fill bottles AND cups with water at different levels for a full 8-note scale!",
        "steps": [
            "Line up 4 glass bottles and 4 cups.",
            "Fill with increasing amounts of water (less = higher pitch).",
            "Add food colouring to each container for a rainbow display.",
            "Tap bottles with a metal spoon, cups with a wooden one.",
            "Try to play a simple song like 'Mary Had a Little Lamb'!",
        ],
        "materials": ["bottle", "cup", "water", "spoon", "food coloring"],
    },

    frozenset({"scissors", "vase"}): {
        "title": "Fabric-Wrap Vase",
        "emoji": "🌸",
        "difficulty": "Easy",
        "time_est": "20 mins",
        "tagline": "COMBO UNLOCK! Snip fabric strips and weave them around the vase for a cosy textile look!",
        "steps": [
            "Cut old fabric or T-shirts into 2 cm wide strips.",
            "Apply a thin layer of craft glue to a section of the vase.",
            "Wrap strips tightly around, overlapping edges slightly.",
            "Apply a coat of glue over the top to seal.",
            "Let dry — the fabric becomes stiff and beautifully decorative!",
        ],
        "materials": ["scissors", "vase", "fabric", "craft glue", "brush"],
    },

    frozenset({"couch", "tv"}): {
        "title": "Couch Cinema Night",
        "emoji": "🍿",
        "difficulty": "Easy",
        "time_est": "20 mins",
        "tagline": "COMBO UNLOCK! Transform your couch into a VIP movie lounge with handmade tickets and snacks!",
        "steps": [
            "Design and cut paper 'VIP cinema tickets' for everyone.",
            "Arrange couch cushions into a comfy theatre seating layout.",
            "Dim the lights and put blankets on every seat.",
            "Prepare popcorn in a big bowl (the 'cinema snack bar').",
            "Pick a movie, dim the lights, and enjoy the show!",
        ],
        "materials": ["couch", "tv", "paper", "scissors", "popcorn", "blankets"],
    },

    frozenset({"apple", "carrot"}): {
        "title": "Veggie & Fruit Stamp Rainbow",
        "emoji": "🌈",
        "difficulty": "Easy",
        "time_est": "20 mins",
        "tagline": "COMBO UNLOCK! Use apple halves and carrot rounds as rainbow stamps across a big canvas!",
        "steps": [
            "Cut apple in half and carrot into various round slices.",
            "Set up 7 colours of paint in a rainbow arc on a palette.",
            "Stamp apple halves for large arcs, carrot rounds for dots.",
            "Work from red on the outside to violet on the inside.",
            "Add handprint clouds and display your rainbow artwork!",
        ],
        "materials": ["apple", "carrot", "paint", "paper", "brush"],
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
    1. Combo projects are surfaced first (score = 1000) when ALL required
       objects in a frozenset key appear in detected_names.
    2. Single-object projects are scored by the count of their `materials`
       list items that also appear in detected_names (partial matches allowed).
    3. Ties are broken by insertion order (predictable, deterministic).

    A project will not appear more than once (duplicate titles are filtered).
    """
    detected_set = set(detected_names)
    results: list[dict] = []
    seen_titles: set[str] = set()

    # ── Step 1: Combo projects (highest priority) ──────────────────────────
    for key_set, project in COMBO_MAP.items():
        if key_set <= detected_set:          # all combo items are present
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
