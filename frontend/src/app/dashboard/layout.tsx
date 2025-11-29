import Header from "@/components/dashboard/header";
import { Sidebar } from "@/components/dashboard/sidebar";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <>
            <div className="hidden flex-col md:flex">
                <Header />
                <div className="flex-1 space-y-4 p-8 pt-6">
                    <div className="flex flex-col md:flex-row">
                        <aside className="hidden w-[200px] flex-col md:flex">
                            <Sidebar />
                        </aside>
                        <main className="flex w-full flex-1 flex-col overflow-hidden">
                            {children}
                        </main>
                    </div>
                </div>
            </div>
        </>
    );
}
