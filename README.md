# Encode-AI-Hackathon
Welcome to the Moviefy! 🎬🍿🎥

First platform that generates film-like trailers from your favourite books.

How does it work?
Simply upload a PDF file through the web app and...

Wait for the magic powered by Stability.ai to do its work.


- Did
    - Run models locally
        - Models
            - txt2img: sd_xl_base_0.9, sd_xl_base_1.0
            - img2vid: svd_xt, svd_xt_1_1
        - Challenges
            - Long download time
            - Long model loading (init) time
            - img2vid
                - low resolution : 256x256
            - txt2img
                - query engineering
- Trying to
    - Combining into txt2vid in one single model

