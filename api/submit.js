export default async function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader(
        'Access-Control-Allow-Headers',
        'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
    );

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { firstname, lastname, email, phone, restaurant, locations, notes } = req.body;

        // Retrieve the secure Discord Webhook from environment variables
        const webhookUrl = process.env.DISCORD_WEBHOOK;
        if (!webhookUrl) {
            return res.status(500).json({ error: 'Server configuration error: Webhook not found.' });
        }

        const payload = {
            embeds: [{
                title: "🚀 New Kitchio Demo Request!",
                color: 14117702, // #D76B46 brand terracotta
                fields: [
                    { name: "👤 Contact Name", value: `${firstname} ${lastname}`, inline: true },
                    { name: "🏢 Restaurant", value: restaurant, inline: true },
                    { name: "📍 Locations", value: `${locations} location(s)`, inline: true },
                    { name: "📧 Email", value: email, inline: true },
                    { name: "📱 Phone", value: phone, inline: true },
                    { name: "📝 Notes", value: notes || "*None provided*" }
                ],
                timestamp: new Date().toISOString(),
                footer: {
                    text: "Kitchio Lead Capture System"
                }
            }]
        };

        const response = await fetch(webhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Discord API responded with status ${response.status}`);
        }

        return res.status(200).json({ success: true });
    } catch (error) {
        console.error('Error submitting to Discord:', error);
        return res.status(500).json({ error: 'Failed to process lead submission' });
    }
}
