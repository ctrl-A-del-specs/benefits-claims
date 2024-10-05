# UK Benefits and Claims Assistant

The UK Benefits and Claims Assistant simplifies the process of querying information on various UK benefits and claims, improving accessibility and reducing the time it takes for users to get crucial answers. The integration of AI with a robust dataset enables the tool to serve as a reliable resource for citizens navigating these processes.

## Problem Description

Navigating the complex landscape of the UK benefits and claims system can be overwhelming, especially for individuals who need immediate and accurate information regarding their eligibility or rights. Whether it's updating benefit information, understanding NHS negligence claims, or filing for medical compensation, the system often leaves people with unanswered questions. Delays in receiving this information can lead to missed deadlines, incomplete filings, and unclaimed benefits.

The **UK Benefits and Claims Assistant** project addresses this issue by providing a user-friendly RAG (Retrieval-Augmented Generation) application. This assistant allows users to ask questions related to UK benefits, claims, and NHS negligence claims. By leveraging a pre-processed dataset and advanced AI models, it offers accurate, real-time answers on various topics like managing existing benefits, medical negligence claims, and statutory sick pay.

## Data

The dataset used in this project has been generated and compiled using ChatGPT. It consists of 425 records and is stored in the `data/claims.csv` file. The dataset is structured into four columns:

- **category**: The type of claim or benefit (e.g., general claim benefits, NHS claim benefits).
- **question**: Frequently asked questions (e.g., "How do I update my benefit information?").
- **answer**: The corresponding answers (e.g., "You can update your benefit information online through your account.").
- **section**: The section of the claims system it applies to (e.g., "general claim benefits" or "NHS claim benefits").

Here’s a snippet of the dataset:

```csv
category,question,answer,section
Manage existing benefit,How do I update my benefit information?,You can update your benefit information online through your account.,general claim benefits
Causation,What is the role of a second opinion in establishing causation?,A second opinion can provide critical evidence in establishing that the initial care was negligent and caused harm.,nhs claim benefits
Limitation,How does the limitation period apply to claims for minors?,The limitation period for minors typically begins when they turn 18 giving them until they are 21 to file a claim.,nhs claim benefits
Temporarily unable to work,How do I claim SSP?,Statutory Sick Pay is claimed through your employer if you’re too ill to work.,general claim benefits
Families,What is the Childcare Grant?,The Childcare Grant is available to students in full-time higher education who have children.,general claim benefits

## USAGE

```
git clone <https://github.com/KayA-ctrl/uk-benefit-assistant>
cd uk-benefits-claims-assistant
```