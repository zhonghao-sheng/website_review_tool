# website-review-tool
A tool that can review a defined range of UoM websites (internal and external), and detect thing like broken links and specified text or other user defined content, and return results which highlight hits and link to impacted pages to facilitate repair and update (currently, we need to eyeball webpages and click hundreds of links to check this – given structure of UoM websites this makes keeping webisted up to date virtually impossible). As an extension, if the tool could do the same for documents stored in a SharePoint site, that would be super ace.

## Features

- Review public and UniMelb restricted websites for broken links and specific keywords
- Supports authentication using Okta Verify for accessing restricted UniMelb websites
- Allows users to review documents stored in a SharePoint site
- Custom keyword and content detection

## Setup Instructions

### 1. Access the Web Application
To use the web application, simply click on the provided link: [Website Review Tool](http://env1.eba-wy6fcmup.ap-southeast-2.elasticbeanstalk.com/). No local setup is required as this is a hosted web app.

### 2. User Registration and Login
- Register as a user to access public websites.
- UniMelb-specific and restricted content will require you to have a valid UniMelb account.
- Use Okta Verify for secure login when accessing UniMelb-restricted pages.

## Repository Structure

```
├── .ebextensions/
├── .github/workflows/
├── .idea/
├── .platform/nginx/conf.d/
├── apps/
│   ├── login/               # Handles user authentication, login, and logout
│   └── search_link/         # Handles search functionality and link review
├── resources/ui_component/   # UI components for the frontend
├── static/
├── staticfiles/admin/
├── templates/                # HTML templates for rendering web pages
├── website_review_tool/       # Main project folder
│   └── __init__.py
├── .gitattributes
├── .gitignore
├── Pipfile
├── README.md
├── manage.py                 # Django project management file
└── requirements.txt          # Python dependencies for the project
```

## Technologies Used

- **Django** - Backend framework
- **Okta Verify** - Secure authentication for restricted content
- **AWS Elastic Beanstalk** - Deployment platform
- **AWS RDS (MySQL)** - Relational database service
