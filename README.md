# Betbay

## **Project Overview**

The web application is a betting platform where **Admins** manage betting groups, user accounts, transactions, and system settings. **Bettors** (registered users) can view betting groups, purchase bundles, manage their stakes, and handle financial transactions like deposits and withdrawals. The platform ensures secure operations through features like user authentication, KYC verification, and transaction monitoring.

## **Use Cases**

### **1. Admin Use Cases**

Admins have comprehensive control over the platform, including managing betting groups, user accounts, financial transactions, and system settings. Below are the detailed features available to Admins:

#### **a. Dashboard Management**

- **Total Users**: View the total number of registered users on the platform.
- **Active Users**: Monitor users who are currently active.
- **Email Unverified Users**: Track users who haven't verified their email addresses.
- **Mobile Unverified Users**: Identify users who haven't verified their mobile numbers.

- **Deposits Overview**:
  - **Total Deposited**: Total amount deposited by all users.
  - **Pending Deposits**: Deposits awaiting approval.
  - **Rejected Deposits**: Deposits that have been rejected.
  - **Deposited Charge**: Fees or charges applied to deposits.

- **Withdrawals Overview**:
  - **Total Withdrawn**: Total amount withdrawn by users.
  - **Pending Withdrawals**: Withdrawals awaiting approval.
  - **Rejected Withdrawals**: Withdrawals that have been rejected.
  - **Withdrawal Charge**: Fees or charges applied to withdrawals.

- **Bundles Status**:
  - **Pending Bundles**: Bundles that are yet to be resolved.
  - **Bundles Won**: Bundles that have been won.
  - **Bundles Lost**: Bundles that have been lost.
  - **Refunded Bundles**: Bundles that have been refunded.

- **Reports**:
  - **Deposit Report (Chart)**: Visual representation of deposit activities.
  - **Withdrawal Report (Chart)**: Visual representation of withdrawal activities.

#### **b. Core Menus Management**

##### **i. Manage Groups**

- **Create Betting Groups**: Admins can create new betting groups.
- **Group Details**:
  - **Group Name**: Name of the betting group.
  - **Bundle Price**: Cost of each bundle within the group.
  - **Returns**: Potential returns on winning.
  - **Limit**: Minimum and maximum number of bundles that can be purchased.
  - **Status**: Current state of the group (Running, Upcoming, Closed).
- **Actions**:
  - **Details**: View detailed information about a group.
  - **Pagination, Search, Filter**: Navigate through groups efficiently.
  - **Add New**: Option to add new betting groups.

##### **ii. Manage Bundles**

- **Bundle Management**: Each bundle is specific to one group.
- **Bundle Details**:
  - **User**: The bettor who purchased the bundle.
  - **Stake**: Amount staked on the bundle.
  - **Number of Bundles**: Quantity of bundles purchased.
  - **Potential Wins**:
    - **Minimum Win**: 3x the bundle price.
    - **Maximum Win**: 5x the bundle price.
  - **Status**: Current state of the bundle (Pending, Won, Lost, Refunded).
- **Actions**:
  - **Details**: View detailed information about a bundle.
  - **Pagination, Search, Filter**: Efficiently manage large numbers of bundles.
  - **Add New**: Option to add new bundles.

##### **iii. Manage Users**

- **User Management**:
  - **Active Users**: View and manage currently active users.
  - **Banned Users**: Users who are prohibited from accessing the platform.
  - **Email Unverified Users**: Users who need to verify their email addresses.
  - **Mobile Unverified Users**: Users who need to verify their mobile numbers.
  - **KYC Verified Users**: Users who have completed Know Your Customer (KYC) verification by uploading identification (e.g., NIN slip).
  - **KYC Unverified Users**: Users who have not completed KYC verification.
- **User Details**:
  - **Name, Email, Mobile, Country**: Basic user information.
  - **Joined At**: Date when the user registered.
  - **Balance**: Current account balance of the user.
- **Actions**:
  - **Details**: View detailed information about a user.
  - **Pagination, Search, Filter**: Manage and locate users efficiently.
  - **Add New**: Option to add new users manually.

##### **iv. Manage Finance**

- **Payment Methods**:
  - **Automatic Methods**:
    - **Gateway**: Payment gateway used.
    - **Supported Currency**: Currencies supported by the gateway.
    - **Enabled Currency**: Currencies currently enabled for transactions.
    - **Status**: Active or inactive status of the gateway.
    - **Actions**: View details, paginate, search.
  - **Manual Methods**:
    - **Gateway**: Payment gateway used.
    - **Status**: Active or inactive status.
    - **Actions**: View details, paginate, search, add new methods.

- **Deposits Management**:
  - **Pending Deposits**: Deposits awaiting admin approval.
  - **Approved Deposits**: Deposits that have been approved.
  - **Successful Deposits**: Deposits that have been completed successfully.
  - **Rejected Deposits**: Deposits that have been rejected.
  - **Initiated Deposits**: Deposits that have been initiated but not yet processed.
  - **All Deposits**: View all deposit transactions.
  - **Deposit Details**:
    - **Gateway, Transaction ID**: Payment details.
    - **Initiated By**: User who made the deposit.
    - **Amount**: Total amount deposited.
    - **Conversion Rate**: Naira to Dollar rate at the time of deposit.
    - **Status**: Current status of the deposit (Pending, Approved, Successful, Rejected).

- **Withdrawals Management**:
  - **Pending Withdrawals**: Withdrawals awaiting admin approval.
  - **Approved Withdrawals**: Withdrawals that have been approved.
  - **Rejected Withdrawals**: Withdrawals that have been rejected.
  - **All Withdrawals**: View all withdrawal transactions.
  - **Withdrawal Details**:
    - **Gateway, Transaction ID**: Payment details.
    - **Initiated By**: User who requested the withdrawal.
    - **Amount**: Total amount withdrawn.
    - **Conversion Rate**: Naira to Dollar rate at the time of withdrawal.
    - **Status**: Current status of the withdrawal (Pending, Approved, Successful, Rejected).

#### **c. Platform Management**

##### **i. System Settings**

- **Configuration**: Manage various system settings, such as site configurations, security settings, and application preferences.

##### **ii. Support Tickets**

- **Ticket Management**:
  - **Pending Tickets**: Tickets awaiting admin response.
  - **Closed Tickets**: Tickets that have been resolved and closed.
  - **Answered Tickets**: Tickets that have been responded to but not yet closed.
  - **All Tickets**: View all support tickets.
- **Ticket Details**:
  - **Subject**: Topic of the complaint or query.
  - **Submitted By**: User who submitted the ticket.
  - **Status**: Current status of the ticket (Open, Closed, Answered).
  - **Priority**: Level of urgency (e.g., High).
  - **Last Reply**: Most recent response in the ticket thread.
  - **Actions**: Pagination, search for efficient ticket management.

##### **iii. Reports**

- **Transaction History**:
  - **User**: The user involved in the transaction.
  - **Transaction ID**: Unique identifier for the transaction.
  - **Date**: When the transaction occurred.
  - **Amount**: Amount involved in the transaction.
  - **Post Balance**: User's balance after the transaction.
  - **Features**: Pagination, search (by transaction ID or user name), date filtering.

- **User Login History**:
  - **User**: The user who logged in.
  - **Login At**: Timestamp of the login.
  - **IP Address**: IP from which the user logged in.
  - **Location**: Geographical location of the login.
  - **Browser**: Browser used for the login.
  - **Features**: Pagination, search, date filtering.

- **Notification History**:
  - **User**: The user who received the notification.
  - **Sent At**: Timestamp when the notification was sent.
  - **Sender**: Admin who sent the notification.
  - **Subject**: Topic of the notification.
  - **Features**: Pagination, search, date filtering.

#### **d. Notifications Management**

- **Send Notifications**: Admins can send messages to all users or select groups via the admin interface. Notifications are delivered to users' email addresses.

---

### **2. Bettors (Users) Use Cases**

Bettors interact with the platform to view betting groups, purchase bundles, manage their stakes, handle financial transactions, and communicate with support. Below are the detailed features available to Bettors:

#### **a. User Registration and Authentication**

- **Registration**:
  - **Sign Up with Email**: Users can create an account using their email address.
  - **Include Recaptcha**: Security feature to prevent bots from registering.
  - **Login with Phone Number**: Users can log in using their phone number, which triggers an OTP (One-Time Password) for verification.
  - **KYC Identity Verification**: Users must complete KYC verification during signup by providing identification (e.g., NIN slip).

- **Login History**:
  - **Recorded Activity**: Every login is recorded for security and audit purposes, including IP address, location, and browser used.

#### **b. Viewing and Managing Betting Groups**

- **View Running Groups**: Users can see all currently active betting groups, including details like group name, bundle price, potential returns, and status.
- **View Closed Groups**: Users can view groups that have been closed by the admin.
- **View All Groups**: Comprehensive list of all betting groups, regardless of their status.
- **Search and Filter Groups**: Users can search for specific groups or filter them based on criteria like status or bundle price.

#### **c. Purchasing Bundles**

- **Buy Bundle**:
  - **Select Group**: Choose a betting group to purchase bundles from.
  - **Select Bundle Quantity**: Purchase a specific number of bundles within the allowed limits set by the admin (minimum and maximum).
  - **Stake Amount**: The total cost calculated as the number of bundles multiplied by the bundle price.

- **Potential Wins Calculation**:
  - **Minimum Potential Win**: 3x the bundle price per bundle.
  - **Maximum Potential Win**: 5x the bundle price per bundle.
  - **Example**: If a bundle costs ₦5,000 and a user buys 10 bundles, the potential win ranges from ₦150,000 (10 x ₦15,000) to ₦250,000 (10 x ₦25,000).

- **View Purchased Bundles**:
  - **List of Bundles**: Users can see all their staked bundles, including status and bundle information.
  - **Bundle Status**: Pending, Won, Lost, or Refunded.

#### **d. Financial Transactions**

- **Deposits**:
  - **Make a Deposit**: Users can deposit funds into the platform's account number when staking or purchasing bundles.
  - **Provide Deposit Information**: Details about the deposit are provided and visible to the admin for confirmation.

- **Withdrawals**:
  - **Initiate Withdrawal**: Users can request to withdraw their winnings.
  - **Withdrawal Processing**: Admin reviews and credits the amount to the user's provided bank account upon approval.

#### **e. Notifications and Communication**

- **Receive Notifications**:
  - **Notification Page**: Users have a dedicated page to view all activities related to their account, including:
    - Bundles purchased
    - Bundles won or lost
    - Transaction details (deposits and withdrawals)
    - Other relevant updates

- **Support Tickets**:
  - **Create a Ticket**: Users can create support tickets to complain about issues or seek assistance.
  - **Ticket Tracking**: Users can view the status of their tickets and any responses from the admin.

#### **f. Account Management**

- **View Account Details**:
  - **Profile Information**: Users can view and update their personal information.
  - **Balance Overview**: Current balance reflecting deposits and withdrawals.

- **Manage Staked Bundles**:
  - **List of Bundles**: View all staked bundles with their current status and potential wins.

---

## **Feature Documentation Summary**

### **Admin Features**

1. **Dashboard Management**: Overview of users, deposits, withdrawals, and bundle statuses with visual reports.
2. **Manage Groups**: Create and manage betting groups with specific bundle prices and limits.
3. **Manage Bundles**: Oversee all bundles purchased by users, set their status, and calculate potential wins.
4. **Manage Users**: Control user accounts, including verification, banning, and KYC status.
5. **Manage Finance**: Handle all financial aspects, including payment methods, deposits, and withdrawals.
6. **Platform Management**: Configure system settings, manage support tickets, and generate reports.
7. **Notifications Management**: Send out notifications to users via email.

### **Bettor (User) Features**

1. **Registration and Authentication**: Secure sign-up and login process with email, phone number, Recaptcha, and KYC verification.
2. **View Betting Groups**: Access information on running, closed, and all betting groups.
3. **Purchase Bundles**: Buy bundles within set limits and view potential winnings.
4. **Manage Financial Transactions**: Deposit funds for staking and request withdrawals for winnings.
5. **Receive Notifications**: Stay informed about account activities and platform updates.
6. **Support Tickets**: Communicate issues or seek help through support tickets.
7. **Account Management**: View and manage personal account details and staked bundles.

----------------------------------------

Absolutely! To develop a robust and scalable betting web application like **Betbay**, it's crucial to design a well-structured database schema. This schema will define the tables, their fields, and the relationships between them, ensuring that all features operate seamlessly. Below is a comprehensive breakdown of the necessary database tables, their fields, data types, primary and foreign keys, along with the relationships between them.

---

## **Database Schema Overview**

The database schema for **Betbay** encompasses several interconnected tables designed to handle user management, betting operations, financial transactions, support, notifications, and system configurations. Below is a detailed description of each table, including their fields and relationships.

---

### **1. Users**

**Purpose:** Stores information about registered bettors on the platform.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `user_id`           | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each user.         |
| `name`              | VARCHAR(255)        | Not Null                               | Full name of the user.                   |
| `email`             | VARCHAR(255)        | Not Null, Unique                       | User's email address.                    |
| `password_hash`     | VARCHAR(255)        | Not Null                               | Hashed password for security.            |
| `mobile_number`     | VARCHAR(20)         | Not Null, Unique                       | User's mobile phone number.              |
| `country`           | VARCHAR(100)        | Not Null                               | Country of residence.                    |
| `email_verified`    | BOOLEAN             | Default: `false`                       | Indicates if the email is verified.      |
| `mobile_verified`   | BOOLEAN             | Default: `false`                       | Indicates if the mobile is verified.     |
| `kyc_verified`      | BOOLEAN             | Default: `false`                       | Indicates if KYC is completed.           |
| `balance`           | DECIMAL(15, 2)      | Default: `0.00`                        | Current account balance in Naira.        |
| `created_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Account creation timestamp.              |
| `updated_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Last update timestamp.                   |

**Relationships:**

- **One-to-Many** with `UserBundles`: A user can purchase multiple bundles.
- **One-to-Many** with `Deposits` and `Withdrawals`: A user can have multiple deposit and withdrawal transactions.
- **One-to-Many** with `SupportTickets`: A user can create multiple support tickets.
- **One-to-Many** with `Notifications`: A user can receive multiple notifications.
- **One-to-Many** with `LoginHistory`: A user can have multiple login records.
- **One-to-One** with `KYC`: A user can have one KYC record.

---

### **2. Admins**

**Purpose:** Stores information about platform administrators.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `admin_id`          | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each admin.        |
| `name`              | VARCHAR(255)        | Not Null                               | Full name of the admin.                   |
| `email`             | VARCHAR(255)        | Not Null, Unique                       | Admin's email address.                    |
| `password_hash`     | VARCHAR(255)        | Not Null                               | Hashed password for security.             |
| `role`              | VARCHAR(50)         | Not Null                               | Role of the admin (e.g., Super Admin).    |
| `created_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Admin account creation timestamp.         |
| `updated_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Last update timestamp.                    |

**Relationships:**

- **One-to-Many** with `Notifications`: An admin can send multiple notifications.
- **One-to-Many** with `KYC`: An admin can review multiple KYC records.
- **One-to-Many** with `SupportTickets`: An admin can respond to multiple support tickets.

---

### **3. BettingGroups**

**Purpose:** Defines different betting groups available for users to participate in.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `group_id`          | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each betting group.|
| `group_name`        | VARCHAR(255)        | Not Null, Unique                       | Name of the betting group.                |
| `bundle_price`      | DECIMAL(15, 2)      | Not Null                               | Price per bundle in Naira.                |
| `returns_min`       | DECIMAL(15, 2)      | Not Null                               | Minimum return (3x bundle price).         |
| `returns_max`       | DECIMAL(15, 2)      | Not Null                               | Maximum return (5x bundle price).         |
| `min_bundles`       | INT                 | Not Null                               | Minimum number of bundles purchasable.    |
| `max_bundles`       | INT                 | Not Null                               | Maximum number of bundles purchasable.    |
| `status`            | ENUM('Running','Upcoming','Closed') | Not Null, Default: 'Running' | Current status of the group.               |
| `created_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Group creation timestamp.                 |
| `updated_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Last update timestamp.                    |

**Relationships:**

- **One-to-Many** with `UserBundles`: A group can have multiple bundle purchases.

---

### **4. UserBundles**

**Purpose:** Tracks bundles purchased by users within specific betting groups.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `user_bundle_id`    | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each bundle purchase.|
| `user_id`           | UUID / INT          | Foreign Key → `Users.user_id`          | Reference to the purchasing user.         |
| `group_id`          | UUID / INT          | Foreign Key → `BettingGroups.group_id` | Reference to the betting group.           |
| `bundle_price`      | DECIMAL(15, 2)      | Not Null                               | Price per bundle at purchase time.        |
| `quantity`          | INT                 | Not Null                               | Number of bundles purchased.               |
| `stake_amount`      | DECIMAL(15, 2)      | Not Null                               | Total amount staked (quantity × bundle price).|
| `potential_win_min` | DECIMAL(15, 2)      | Not Null                               | Minimum potential win (3x per bundle).    |
| `potential_win_max` | DECIMAL(15, 2)      | Not Null                               | Maximum potential win (5x per bundle).    |
| `status`            | ENUM('Pending','Won','Lost','Refunded') | Not Null, Default: 'Pending' | Current status of the bundle purchase.     |
| `created_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Purchase timestamp.                        |
| `updated_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Last update timestamp.                     |

**Relationships:**

- **Many-to-One** with `Users`: Each bundle purchase is made by one user.
- **Many-to-One** with `BettingGroups`: Each bundle purchase is associated with one betting group.

---

### **5. PaymentMethods**

**Purpose:** Defines the various payment gateways and methods available for deposits and withdrawals.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `gateway_id`        | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each payment gateway.|
| `name`              | VARCHAR(255)        | Not Null, Unique                       | Name of the payment gateway (e.g., Paystack).|
| `type`              | ENUM('Automatic','Manual') | Not Null                       | Type of payment method.                   |
| `supported_currencies` | VARCHAR(50)      | Not Null                               | Currencies supported by the gateway (e.g., "NGN, USD").|
| `enabled_currencies`   | VARCHAR(50)      | Not Null                               | Currently enabled currencies (e.g., "NGN").|
| `status`            | ENUM('Active','Inactive') | Not Null, Default: 'Active'       | Current status of the payment gateway.    |
| `created_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Gateway creation timestamp.               |
| `updated_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Last update timestamp.                    |

**Relationships:**

- **One-to-Many** with `Deposits` and `Withdrawals`: Each payment method can be used for multiple transactions.

---

### **6. Deposits**

**Purpose:** Records all deposit transactions made by users.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `deposit_id`        | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each deposit.       |
| `user_id`           | UUID / INT          | Foreign Key → `Users.user_id`          | Reference to the user making the deposit. |
| `gateway_id`        | UUID / INT          | Foreign Key → `PaymentMethods.gateway_id` | Payment gateway used for the deposit.    |
| `transaction_id`    | VARCHAR(255)        | Not Null, Unique                       | Unique transaction identifier from gateway.|
| `amount`            | DECIMAL(15, 2)      | Not Null                               | Amount deposited in Naira.                |
| `charge`            | DECIMAL(15, 2)      | Default: `0.00`                        | Fees or charges applied to the deposit.   |
| `total_amount`      | DECIMAL(15, 2)      | Computed: `amount + charge`            | Total amount after charges.               |
| `status`            | ENUM('Pending','Approved','Successful','Rejected') | Not Null, Default: 'Pending' | Current status of the deposit.           |
| `initiated_at`     | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Timestamp when the deposit was initiated. |
| `approved_at`       | TIMESTAMP           | Nullable                               | Timestamp when the deposit was approved.  |
| `rejected_at`       | TIMESTAMP           | Nullable                               | Timestamp when the deposit was rejected.  |
| `conversion_rate`   | DECIMAL(10, 4)      | Nullable                               | Naira to Dollar rate at the time of deposit.|
| `created_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Record creation timestamp.                |
| `updated_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Last update timestamp.                    |

**Relationships:**

- **Many-to-One** with `Users`: Each deposit is made by one user.
- **Many-to-One** with `PaymentMethods`: Each deposit uses one payment gateway.

---

### **7. Withdrawals**

**Purpose:** Records all withdrawal transactions requested by users.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `withdrawal_id`     | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each withdrawal.    |
| `user_id`           | UUID / INT          | Foreign Key → `Users.user_id`          | Reference to the user requesting withdrawal.|
| `gateway_id`        | UUID / INT          | Foreign Key → `PaymentMethods.gateway_id` | Payment gateway used for the withdrawal. |
| `transaction_id`    | VARCHAR(255)        | Not Null, Unique                       | Unique transaction identifier from gateway.|
| `amount`            | DECIMAL(15, 2)      | Not Null                               | Amount to be withdrawn in Naira.          |
| `charge`            | DECIMAL(15, 2)      | Default: `0.00`                        | Fees or charges applied to the withdrawal.|
| `total_amount`      | DECIMAL(15, 2)      | Computed: `amount + charge`            | Total amount after charges.               |
| `status`            | ENUM('Pending','Approved','Successful','Rejected') | Not Null, Default: 'Pending' | Current status of the withdrawal.         |
| `initiated_at`     | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Timestamp when the withdrawal was initiated.|
| `approved_at`       | TIMESTAMP           | Nullable                               | Timestamp when the withdrawal was approved.|
| `rejected_at`       | TIMESTAMP           | Nullable                               | Timestamp when the withdrawal was rejected.|
| `conversion_rate`   | DECIMAL(10, 4)      | Nullable                               | Naira to Dollar rate at the time of withdrawal.|
| `created_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Record creation timestamp.                |
| `updated_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Last update timestamp.                    |

**Relationships:**

- **Many-to-One** with `Users`: Each withdrawal is requested by one user.
- **Many-to-One** with `PaymentMethods`: Each withdrawal uses one payment gateway.

---

### **8. SupportTickets**

**Purpose:** Handles user support requests and issues.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `ticket_id`         | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each support ticket.|
| `user_id`           | UUID / INT          | Foreign Key → `Users.user_id`          | Reference to the user who submitted the ticket.|
| `subject`           | VARCHAR(255)        | Not Null                               | Subject of the support ticket.            |
| `description`       | TEXT                | Not Null                               | Detailed description of the issue.        |
| `status`            | ENUM('Open','Closed','Answered') | Not Null, Default: 'Open' | Current status of the ticket.             |
| `priority`          | ENUM('High','Medium','Low') | Not Null, Default: 'Medium' | Priority level of the ticket.             |
| `last_reply_at`    | TIMESTAMP           | Nullable                               | Timestamp of the last reply.              |
| `created_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Ticket creation timestamp.                |
| `updated_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Last update timestamp.                    |

**Relationships:**

- **Many-to-One** with `Users`: Each support ticket is submitted by one user.
- **One-to-Many** with `SupportTicketReplies` (if implementing replies).

---

### **9. Notifications**

**Purpose:** Manages notifications sent to users regarding their activities and platform updates.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `notification_id`   | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each notification.  |
| `user_id`           | UUID / INT          | Foreign Key → `Users.user_id`          | Reference to the recipient user.          |
| `sender_id`         | UUID / INT          | Foreign Key → `Admins.admin_id`        | Reference to the admin who sent the notification. Can be `NULL` for system notifications.|
| `subject`           | VARCHAR(255)        | Not Null                               | Subject of the notification.              |
| `message`           | TEXT                | Not Null                               | Content of the notification.              |
| `sent_at`           | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Timestamp when the notification was sent.|
| `read_at`           | TIMESTAMP           | Nullable                               | Timestamp when the user read the notification.|

**Relationships:**

- **Many-to-One** with `Users`: Each notification is sent to one user.
- **Many-to-One** with `Admins`: Each notification can be sent by one admin.

---

### **10. LoginHistory**

**Purpose:** Logs all user login activities for security and audit purposes.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `login_id`          | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each login record.  |
| `user_id`           | UUID / INT          | Foreign Key → `Users.user_id`          | Reference to the user who logged in.       |
| `login_at`          | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Timestamp of the login event.              |
| `ip_address`        | VARCHAR(45)         | Not Null                               | IP address from which the user logged in.  |
| `location`          | VARCHAR(255)        | Nullable                               | Geographical location of the login.        |
| `browser`           | VARCHAR(255)        | Nullable                               | Browser used during the login.             |
| `device`            | VARCHAR(255)        | Nullable                               | Device type used for the login (e.g., Mobile, Desktop).|

**Relationships:**

- **Many-to-One** with `Users`: Each login record is associated with one user.

---

### **11. KYC**

**Purpose:** Manages Know Your Customer (KYC) verification documents submitted by users.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `kyc_id`            | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each KYC record.     |
| `user_id`           | UUID / INT          | Foreign Key → `Users.user_id`          | Reference to the user undergoing KYC.      |
| `document_type`     | VARCHAR(100)        | Not Null                               | Type of document submitted (e.g., NIN Slip).|
| `document_image`    | VARCHAR(255)        | Not Null                               | URL or path to the uploaded document image.|
| `status`            | ENUM('Pending','Approved','Rejected') | Not Null, Default: 'Pending' | Current status of the KYC verification.     |
| `submitted_at`      | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Timestamp when the document was submitted. |
| `reviewed_at`       | TIMESTAMP           | Nullable                               | Timestamp when the document was reviewed.  |
| `reviewed_by`      | UUID / INT          | Foreign Key → `Admins.admin_id`        | Admin who reviewed the KYC document.        |
| `comments`          | TEXT                | Nullable                               | Admin's comments or reasons for rejection.  |

**Relationships:**

- **One-to-One** with `Users`: Each user can have one KYC record.
- **Many-to-One** with `Admins`: Each KYC review is performed by one admin.

---

### **12. Reports**

**Purpose:** Facilitates the generation of various reports based on transactional and user data. Typically, reports are generated dynamically from existing data and may not require dedicated tables. However, if you wish to store generated reports, consider the following structure.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `report_id`         | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each report.         |
| `report_type`       | VARCHAR(100)        | Not Null                               | Type of report (e.g., Deposit, Withdrawal, Transaction History).|
| `generated_by`      | UUID / INT          | Foreign Key → `Admins.admin_id`        | Admin who generated the report.            |
| `generated_at`      | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Timestamp when the report was generated.   |
| `file_path`         | VARCHAR(255)        | Not Null                               | Path or URL to the generated report file.  |
| `parameters`        | JSON                | Nullable                               | Parameters used to generate the report (e.g., date range).|

**Relationships:**

- **Many-to-One** with `Admins`: Each report is generated by one admin.

---

### **13. SystemSettings**

**Purpose:** Stores various system-wide configurations and settings.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `setting_id`        | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each setting.        |
| `key`               | VARCHAR(255)        | Not Null, Unique                       | Unique key for the setting (e.g., "site_name").|
| `value`             | TEXT                | Not Null                               | Value of the setting.                      |
| `description`       | TEXT                | Nullable                               | Description of what the setting controls.  |
| `updated_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Last update timestamp.                     |

**Relationships:**

- Typically, no direct relationships. Settings are global.

---

### **14. NotificationHistory**

**Purpose:** Logs all notifications sent to users for audit and tracking purposes.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `history_id`        | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each notification history record.|
| `user_id`           | UUID / INT          | Foreign Key → `Users.user_id`          | Reference to the user who received the notification.|
| `sender_id`         | UUID / INT          | Foreign Key → `Admins.admin_id`        | Admin who sent the notification.           |
| `subject`           | VARCHAR(255)        | Not Null                               | Subject of the notification.               |
| `message`           | TEXT                | Not Null                               | Content of the notification.               |
| `sent_at`           | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Timestamp when the notification was sent. |
| `read_at`           | TIMESTAMP           | Nullable                               | Timestamp when the user read the notification.|

**Relationships:**

- **Many-to-One** with `Users`: Each history record is for one user.
- **Many-to-One** with `Admins`: Each history record can be associated with one admin sender.

---

### **15. BundlesStatusHistory** *(Optional)*

**Purpose:** Tracks the history of status changes for each bundle purchase.

| **Field Name**      | **Data Type**       | **Constraints**                        | **Description**                          |
|---------------------|---------------------|----------------------------------------|------------------------------------------|
| `history_id`        | UUID / INT          | Primary Key, Auto-increment (if INT)   | Unique identifier for each status history record.|
| `user_bundle_id`    | UUID / INT          | Foreign Key → `UserBundles.user_bundle_id` | Reference to the bundle purchase.         |
| `previous_status`   | ENUM('Pending','Won','Lost','Refunded') | Not Null | Previous status before the change.        |
| `new_status`        | ENUM('Pending','Won','Lost','Refunded') | Not Null | New status after the change.             |
| `changed_at`        | TIMESTAMP           | Default: `CURRENT_TIMESTAMP`           | Timestamp when the status was changed.    |
| `changed_by`        | UUID / INT          | Foreign Key → `Admins.admin_id`        | Admin who changed the status.             |
| `comments`          | TEXT                | Nullable                               | Comments or reasons for the status change.|

**Relationships:**

- **Many-to-One** with `UserBundles`: Each history record is associated with one bundle purchase.
- **Many-to-One** with `Admins`: Each history record is associated with one admin.

---

## **Entity-Relationship Diagram (ERD)**

While a textual description provides clarity, visual representation through an ERD can further enhance understanding. Below is a simplified textual version of the ERD, illustrating the primary relationships between tables.

1. **Users**
   - **1 ↔ ∞** `UserBundles`
   - **1 ↔ ∞** `Deposits`
   - **1 ↔ ∞** `Withdrawals`
   - **1 ↔ ∞** `SupportTickets`
   - **1 ↔ ∞** `Notifications`
   - **1 ↔ ∞** `LoginHistory`
   - **1 ↔ 1** `KYC`

2. **Admins**
   - **1 ↔ ∞** `Notifications` (as senders)
   - **1 ↔ ∞** `KYC` (as reviewers)
   - **1 ↔ ∞** `SupportTickets` (as responders)
   - **1 ↔ ∞** `Reports`
   - **1 ↔ ∞** `NotificationHistory`

3. **BettingGroups**
   - **1 ↔ ∞** `UserBundles`

4. **UserBundles**
   - **∞ ↔ 1** `Users`
   - **∞ ↔ 1** `BettingGroups`
   - **1 ↔ ∞** `BundlesStatusHistory`

5. **PaymentMethods**
   - **1 ↔ ∞** `Deposits`
   - **1 ↔ ∞** `Withdrawals`

6. **Deposits & Withdrawals**
   - **∞ ↔ 1** `Users`
   - **∞ ↔ 1** `PaymentMethods`

7. **SupportTickets**
   - **∞ ↔ 1** `Users`
   - **∞ ↔ 1** `Admins` (as responders)

8. **Notifications**
   - **∞ ↔ 1** `Users`
   - **∞ ↔ 1** `Admins` (as senders)

9. **LoginHistory**
   - **∞ ↔ 1** `Users`

10. **KYC**
    - **1 ↔ 1** `Users`
    - **∞ ↔ 1** `Admins`

11. **Reports**
    - **∞ ↔ 1** `Admins`

12. **NotificationHistory**
    - **∞ ↔ 1** `Users`
    - **∞ ↔ 1** `Admins`

13. **BundlesStatusHistory** *(Optional)*
    - **∞ ↔ 1** `UserBundles`
    - **∞ ↔ 1** `Admins`

---

## **Detailed Table Descriptions and Relationships**

Below is a more detailed explanation of each table and their interconnections, ensuring clarity for developers and stakeholders.

### **1. Users Table**

- **Purpose:** Central repository for all registered bettors.
- **Key Fields:** `user_id`, `email`, `mobile_number`.
- **Relationships:** Connects to various transactional and support-related tables.

### **2. Admins Table**

- **Purpose:** Manages administrative functionalities and platform oversight.
- **Key Fields:** `admin_id`, `email`, `role`.
- **Relationships:** Oversees transactions, user verifications, support tickets, and notifications.

### **3. BettingGroups Table**

- **Purpose:** Organizes betting opportunities into distinct groups.
- **Key Fields:** `group_id`, `group_name`, `bundle_price`, `returns_min`, `returns_max`, `min_bundles`, `max_bundles`, `status`.
- **Relationships:** Associates with `UserBundles` to track user participation.

### **4. UserBundles Table**

- **Purpose:** Tracks individual bundle purchases by users within specific groups.
- **Key Fields:** `user_bundle_id`, `user_id`, `group_id`, `quantity`, `stake_amount`, `potential_win_min`, `potential_win_max`, `status`.
- **Relationships:** Links users to betting groups and monitors the status of each purchase.

### **5. PaymentMethods Table**

- **Purpose:** Defines the payment gateways available for financial transactions.
- **Key Fields:** `gateway_id`, `name`, `type`, `supported_currencies`, `enabled_currencies`, `status`.
- **Relationships:** Integrates with `Deposits` and `Withdrawals` to facilitate transactions.

### **6. Deposits Table**

- **Purpose:** Records all user-initiated deposit transactions.
- **Key Fields:** `deposit_id`, `user_id`, `gateway_id`, `transaction_id`, `amount`, `charge`, `status`, `conversion_rate`.
- **Relationships:** Tied to users and payment methods for tracking and verification.

### **7. Withdrawals Table**

- **Purpose:** Manages user requests for withdrawing funds.
- **Key Fields:** `withdrawal_id`, `user_id`, `gateway_id`, `transaction_id`, `amount`, `charge`, `status`, `conversion_rate`.
- **Relationships:** Connected to users and payment methods to process and monitor withdrawals.

### **8. SupportTickets Table**

- **Purpose:** Facilitates user support and issue resolution.
- **Key Fields:** `ticket_id`, `user_id`, `subject`, `description`, `status`, `priority`, `last_reply_at`.
- **Relationships:** Enables communication between users and admins.

### **9. Notifications Table**

- **Purpose:** Sends and tracks notifications to users regarding their activities and platform updates.
- **Key Fields:** `notification_id`, `user_id`, `sender_id`, `subject`, `message`, `sent_at`, `read_at`.
- **Relationships:** Bridges communication from admins to users.

### **10. LoginHistory Table**

- **Purpose:** Enhances security by logging all user login activities.
- **Key Fields:** `login_id`, `user_id`, `login_at`, `ip_address`, `location`, `browser`, `device`.
- **Relationships:** Associates login records with specific users.

### **11. KYC Table**

- **Purpose:** Ensures compliance by verifying user identities.
- **Key Fields:** `kyc_id`, `user_id`, `document_type`, `document_image`, `status`, `submitted_at`, `reviewed_at`, `reviewed_by`, `comments`.
- **Relationships:** Connects KYC records with users and admins for verification processes.

### **12. Reports Table**

- **Purpose:** Stores generated reports for administrative review.
- **Key Fields:** `report_id`, `report_type`, `generated_by`, `generated_at`, `file_path`, `parameters`.
- **Relationships:** Generated by admins for various analytical purposes.

### **13. SystemSettings Table**

- **Purpose:** Manages platform-wide configurations and preferences.
- **Key Fields:** `setting_id`, `key`, `value`, `description`, `updated_at`.
- **Relationships:** Acts independently but influences multiple platform functionalities.

### **14. NotificationHistory Table**

- **Purpose:** Maintains a log of all notifications sent to users.
- **Key Fields:** `history_id`, `user_id`, `sender_id`, `subject`, `message`, `sent_at`, `read_at`.
- **Relationships:** Tracks which users received which notifications and their read status.

### **15. BundlesStatusHistory Table** *(Optional)*

- **Purpose:** Keeps a historical record of status changes for each bundle purchase.
- **Key Fields:** `history_id`, `user_bundle_id`, `previous_status`, `new_status`, `changed_at`, `changed_by`, `comments`.
- **Relationships:** Provides an audit trail linking status changes to specific admins.

---

## **Relationships Summary**

To ensure data integrity and facilitate efficient data retrieval, the following relationships are established:

- **Users ↔ UserBundles:** One user can purchase multiple bundles.
- **BettingGroups ↔ UserBundles:** One betting group can have multiple bundle purchases.
- **Users ↔ Deposits/Withdrawals:** One user can have multiple financial transactions.
- **PaymentMethods ↔ Deposits/Withdrawals:** One payment method can be used for multiple transactions.
- **Users ↔ SupportTickets:** One user can submit multiple support tickets.
- **Admins ↔ SupportTickets:** One admin can respond to multiple support tickets.
- **Users ↔ Notifications:** One user can receive multiple notifications.
- **Admins ↔ Notifications:** One admin can send multiple notifications.
- **Users ↔ LoginHistory:** One user can have multiple login records.
- **Users ↔ KYC:** One user has one KYC record.
- **Admins ↔ KYC:** One admin can review multiple KYC records.
- **Admins ↔ Reports:** One admin can generate multiple reports.
- **Users ↔ NotificationHistory:** One user can have multiple notification history records.
- **Admins ↔ NotificationHistory:** One admin can be associated with multiple notification history records.
- **UserBundles ↔ BundlesStatusHistory:** One bundle purchase can have multiple status history records.
- **Admins ↔ BundlesStatusHistory:**
