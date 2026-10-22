"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { Card, CardContent } from "@/components/ui/card";

type UserData = {
  id: string | number;
  username: string;
  email: string;
  is_admin: boolean;
  permissions: { id: string | number; permission_name: string }[];
};

function AdminPage() {
  const { id } = useParams<{ id: string }>();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserData();
  }, [id]);

  const fetchUserData = async () => {
    setLoading(true);
    const response = await fetch(`http://127.0.0.1:8888/user/${id}`);
    setUserData(response.ok ? await response.json() : null);
    setLoading(false);
  };

  const rows: [string, React.ReactNode][] = userData
    ? [
        ["ID", userData.id],
        ["Username", userData.username],
        ["Email", userData.email],
        ["Admin", String(userData.is_admin)],
        [
          "Permissions",
          <ul key="perms">
            {userData.permissions.map((perm) => (
              <li key={perm.id}>{perm.permission_name}</li>
            ))}
          </ul>,
        ],
      ]
    : [];

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col gap-6 p-4">
      <h2 className="text-2xl font-semibold">DocGenie</h2>
      {loading && <p>Loading...</p>}

      {userData && (
        <Card>
          <CardContent>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="py-2 font-medium">Field</th>
                  <th className="py-2 font-medium">Value</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(([field, value]) => (
                  <tr key={field} className="border-b last:border-0">
                    <td className="py-2 pr-4 text-muted-foreground">{field}</td>
                    <td className="py-2">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </main>
  );
}

export default AdminPage;
