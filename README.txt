NEXT STEPS:

00. Polish website

0. Fledge out Admin control center
    Scheduled broadcast manager
    Edit broadcast information
    Live Broadcast Panel
        Live session controls
            stream status indicator
            embed preview
            scoreboard controls
            live stats (?)



1. Add scoreboard support
    Show a live-updating scoreboard on StreamPage
    Add scoreboard controls (team names, scores) in AdminPage
    Backend will serve current scoreboard state and accept updates

2. Add user login system
    Admins: access to create broadcasts and update scoreboard
    Guests: only view streams (maybe after logging in or pay-per-view)

3. Implement guest paywall
    Could be basic like "Enter access code" or Stripe integration
    Only allow access to streams after payment/verification
    Store paid guess access in database, so they can come back to the stream

4. Set up database
    Using PostgreSQL to store:
        Users (admins and guests)
        Broadcast information and metadata
        Scoreboard state
        Transactions/access controls

5. Deployment
    Deploy backend to Fly.io, Railway, or Render
    Host frontend on GitHub Pages (?), Vercel, or Netlify
    Connect frontend and backend


Archiving streams??