# Where When Pray: A serverless application for prayer time scraping and notification

A website that shows the prayer times for a preconfigured list of masjids in a tabular format. The data is scraped from the masjid websites periodically. Visitors can subscribe to one or more masjids and receive email notifications when the prayer times change.

## Motivation

With each masjid having their own schedule for prayers that also change sometimes every few days, the only way to get accurate information is to visit each masjid's website. This application aims to solve this problem by scraping the prayer times from the masjid websites and notifying the subscribers when the prayer times change. Some solutions, like the awesome TMA or [The Masjid App](https://themasjidapp.net/), already exist but they require the masjid management to update the prayer times on their website, which is not always the case. I decided to create this application to solve this problem for myself and others by offering a simple website that displays all the prayer times in one page.

## Architecture

The application is built using serverless components on AWS:
1. **Scraper**: A Lambda function triggered 4 times a day and scrapes the prayer times from the masjid websites. The data is then stored in a CSV file in S3.
1. **Notifier**: A Lambda function triggered as soon as a new CSV file is created (typically from the Scraper) and compares it to the previous CSV file. If there are any changes, it sends an email notification to the subscribers. Finally, it replaces the previous CSV file with the new one. Each masjid has its own list of subscribers.
1. **Generator**: A Lambda function triggered as soon as a new CSV file is created (typically from the Notifier) and generates a static HTML file from it. The HTML file is then uploaded to S3 and served via CloudFront. The website lists all the masjids and their prayer times in a tabular format. It has a form to subscribe to notifications where it submits to the Subscriber Lambda function (see below).
1. **Subscriber**: A Lambda function triggered when a user submits the subscription form which adds the user to the masjid's list of subscribers.

## Email notifications

Subscribers are stored in Amazon SES as contacts with a separate topic for each masjid. The email notification contains a link in the footer to unsubscribe from the notifications. The link target is handled by SES and allows the user to opt in/out from any topic. The subscription form target adds the user as a new/updated contact to the corresponding topic in Amazon SES. Amazon SES only supports 1 contact list per AWS account and maximum of 20 topics which is good enough at a small scale. For a wider support of masjids, different deployment using separate AWS accounts will be required, unless subscriptions are handled differently.

## Masjids database

Each masjid has its own folder which contains some metadata about the masjid and the code that scrapes its website. This is a simple approach that may be replaced in the future with a more sophisticated solution. To support a wider range of masjids, the code can be modified later to only operate on a subset of the masjids and deployed under different subdomains, where visitors will be typically interested in the masjids in their area.
