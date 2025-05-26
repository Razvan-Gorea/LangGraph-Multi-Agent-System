"use client";
import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import styles from "../../../../styles/Chat_Bot.module.css";
import pageStyles from "../../../../styles/Admin.module.css";
import { Rubik } from "next/font/google";

const rubik = Rubik({
  subsets: ["latin"],
  weight: ["300"],
});

function AdminPage() {
  const { id } = useParams();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState(id || '');
  const router = useRouter();

  useEffect(() => {
    fetchUserData();
  }, [id]);

  const fetchUserData = async () => {
    setLoading(true);
    const response = await fetch(`http://127.0.0.1:8888/user/${id}`);
    if (response.ok){
      const data = await response.json();
      setUserData(data);
    }
    else{
      setUserData(null);
    }
    setLoading(false);
  };

  const handleSearch = () => {
    fetchUserData(userId);
    router.push(`/admin/${userId}`)
  };

    return (
      <main className={rubik.className}>
        <section className={styles.block}>
          <h2> DocGenie </h2>
        </section>
        <section className={pageStyles.container}>
          <div className={pageStyles.searchContainer}>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="Enter User ID"
              className={pageStyles.searchField}
            />
            <button 
              onClick={handleSearch} 
              className={pageStyles.searchButton}
            >
              Search
            </button>
          </div>

          {loading && <p>Loading...</p>}

          {userData && (
            <table className={pageStyles.table}>
              <thead>
                <tr className={pageStyles.tableHeader}>
                  <th className={pageStyles.tableHeaderCell}>Field</th>
                  <th className={pageStyles.tableHeaderCell}>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className={pageStyles.tableCell}>ID</td>
                  <td className={pageStyles.tableCell}>{userData.id}</td>
                </tr>
                <tr>
                  <td className={pageStyles.tableCell}>Username</td>
                  <td className={pageStyles.tableCell}>{userData.username}</td>
                </tr>
                <tr>
                  <td className={pageStyles.tableCell}>Email</td>
                  <td className={pageStyles.tableCell}>{userData.email}</td>
                </tr>
                <tr>
                  <td className={pageStyles.tableCell}>Admin</td>
                  <td className={pageStyles.tableCell}>{String(userData.is_admin)}</td>
                </tr>
                <tr>
                  <td className={pageStyles.tableCell}>Permissions</td>
                  <td className={pageStyles.tableCell}>
                    <ul>
                      {userData.permissions.map(perm => (
                        <li key={perm.id}>{perm.permission_name}</li>
                      ))}
                    </ul>
                  </td>
                </tr>
              </tbody>
            </table>
          )}
        </section>
      </main>
  );
}

export default AdminPage;