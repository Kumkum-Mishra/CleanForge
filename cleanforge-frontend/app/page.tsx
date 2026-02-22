"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [cleaningLoading, setCleaningLoading] = useState(false);

  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [cleanedData, setCleanedData] = useState<any>(null);
  const [cleaningLog, setCleaningLog] = useState<string[]>([]);
  const [qualityAfter, setQualityAfter] = useState<number | null>(null);
  const [improvement, setImprovement] = useState<number | null>(null);

  const [history, setHistory] = useState<
    { name: string; score: number; date: string }[]
  >([]);

  // ------------------ Analyze ------------------
  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setCleanedData(null);
    setCleaningLog([]);
    setQualityAfter(null);
    setImprovement(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error();

      const data = await res.json();
      setResult(data);

      setHistory((prev) => [
        {
          name: file.name,
          score: data.quality_score,
          date: new Date().toLocaleString(),
        },
        ...prev,
      ]);
    } catch {
      setError("Failed to analyze dataset.");
    }

    setLoading(false);
  };

  // ------------------ Clean ------------------
  const handleClean = async () => {
    if (!file) return;

    setCleaningLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/clean`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error();

      const data = await res.json();

      setCleanedData(data.cleaned_preview);
      setCleaningLog(data.cleaning_log);
      setQualityAfter(data.quality_after);
      setImprovement(data.improvement);
    } catch {
      console.error("Cleaning failed");
    }

    setCleaningLoading(false);
  };

  // ------------------ Drag & Drop ------------------
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  // ------------------ Download ------------------
  const downloadCSV = () => {
    if (!cleanedData) return;

    const headers = Object.keys(cleanedData[0]);
    const rows = cleanedData.map((row: any) =>
      headers.map((header) => row[header])
    );

    const csvContent =
      [headers.join(","), ...rows.map((r: any) => r.join(","))].join("\n");

    const blob = new Blob([csvContent], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "cleaned_dataset.csv";
    link.click();
  };

  return (
    <main className="min-h-screen bg-gray-50 text-gray-900 px-8 py-16">

      {/* Header */}
      <div className="max-w-5xl mx-auto mb-12">
        <h1 className="text-6xl font-extrabold tracking-tight leading-[1.05] pb-1 text-transparent bg-clip-text bg-gradient-to-r from-black via-gray-800 to-black">
          CleanForge
        </h1>
        <p className="text-gray-600 mt-3 text-lg">
          Built for teams who clean their own data: profile, fix, and export in minutes.
        </p>
      </div>

      {/* Upload Area */}
      <div className="max-w-3xl mx-auto">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-2xl p-12 text-center transition ${
            dragActive
              ? "border-black bg-white"
              : "border-gray-300 bg-white"
          }`}
        >
          <p className="text-gray-600 mb-4">
            Drag & drop your CSV file here
          </p>

          <label className="inline-block mb-6">
            <input
              type="file"
              accept=".csv"
              onChange={(e) => {
                if (e.target.files) setFile(e.target.files[0]);
              }}
              className="hidden"
            />
            <span className="inline-block bg-gray-100 border-2 border-gray-300 text-gray-800 px-6 py-2 rounded-lg font-medium hover:bg-gray-200 hover:border-gray-400 cursor-pointer transition">
              Choose File
            </span>
          </label>

          <button
            onClick={handleAnalyze}
            className="bg-black text-white px-8 py-3 rounded-xl font-medium hover:bg-gray-800 transition"
          >
            {loading ? "Analyzing..." : "Analyze Dataset"}
          </button>
        </div>
      </div>

      {error && (
        <div className="text-red-500 text-center mt-6">{error}</div>
      )}

      {/* Results Section */}
      {result && (
        <div className="max-w-6xl mx-auto mt-16 space-y-12 animate-fadeIn">

          {/* Quality Score */}
          <div className="bg-black border border-black p-10 rounded-2xl shadow-sm">
            <p className="text-sm uppercase tracking-wider text-white">
              Data Quality Score
            </p>

            <div className="mt-4 text-6xl font-semibold text-white">
              {result?.quality_score}
            </div>
          </div>


          {/* Semantic Analysis */}
          <div className="bg-white border border-gray-200 p-10 rounded-2xl shadow-sm">
            <h2 className="text-2xl font-semibold mb-8">
              Semantic Analysis
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {Object.entries(result.semantic_analysis).map(
                ([column, details]: any) => (
                  <div
                    key={column}
                    className="border border-gray-200 p-6 rounded-xl"
                  >
                    <h3 className="font-semibold text-lg">{column}</h3>
                    <p className="text-gray-500 text-sm mb-4">
                      {details.semantic_type}
                    </p>

                    <div className="text-sm">
                      <strong>Issues</strong>
                      <ul className="list-disc list-inside text-red-500 mt-2">
                        {details.issues_detected.map(
                          (issue: string, i: number) => (
                            <li key={i}>{issue}</li>
                          )
                        )}
                      </ul>
                    </div>

                    <div className="text-sm mt-4">
                      <strong>Suggested Fixes</strong>
                      <ul className="list-disc list-inside text-green-600 mt-2">
                        {details.suggested_fixes.map(
                          (fix: string, i: number) => (
                            <li key={i}>{fix}</li>
                          )
                        )}
                      </ul>
                    </div>
                  </div>
                )
              )}
            </div>

            <div className="text-center mt-10">
              <button
                onClick={handleClean}
                className="bg-black text-white px-10 py-3 rounded-xl hover:bg-gray-800 transition"
              >
                {cleaningLoading ? "Cleaning..." : "Apply Cleaning"}
              </button>
            </div>
          </div>

          {/* Quality Improvement */}
          {cleanedData && (
            <div className="bg-green-50 border border-green-200 p-8 rounded-2xl">
              <h3 className="text-sm uppercase tracking-wide text-green-600">
                Quality Improvement
              </h3>

              <div className="mt-4 text-2xl font-medium">
                {result.quality_score} → {qualityAfter}
                {improvement !== null && (
                  <span className="ml-4 text-green-600">
                    (+{improvement})
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Cleaning Log */}
          {cleaningLog.length > 0 && (
            <div className="bg-white border border-gray-200 p-8 rounded-2xl">
              <h3 className="text-xl font-semibold mb-6">
                Cleaning Log
              </h3>
              <ul className="list-disc list-inside text-gray-700">
                {cleaningLog.map((log, index) => (
                  <li key={index}>{log}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Cleaned Preview */}
          {cleanedData && (
            <div className="bg-white border border-gray-200 p-8 rounded-2xl overflow-auto">
              <h3 className="text-xl font-semibold mb-6">
                Cleaned Preview
              </h3>

              <table className="min-w-full text-sm border border-gray-200">
                <thead className="bg-gray-100">
                  <tr>
                    {Object.keys(cleanedData[0]).map((col) => (
                      <th
                        key={col}
                        className="border px-4 py-2 text-left"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {cleanedData.map((row: any, i: number) => (
                    <tr key={i}>
                      {Object.values(row).map(
                        (val: any, j: number) => (
                          <td
                            key={j}
                            className="border px-4 py-2"
                          >
                            {val?.toString()}
                          </td>
                        )
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="text-right mt-6">
                <button
                  onClick={downloadCSV}
                  className="bg-black text-white px-6 py-2 rounded-lg hover:bg-gray-800 transition"
                >
                  Download Cleaned CSV
                </button>
              </div>
            </div>
          )}

          {history.length > 0 && (
            <div className="bg-white border border-gray-200 p-8 rounded-2xl">
              <h3 className="text-xl font-semibold mb-6">
                Dataset History
              </h3>

              <div className="space-y-4">
                {history.map((item, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 p-4 rounded-xl flex justify-between"
                  >
                    <div>
                      <p className="font-medium">{item.name}</p>
                      <p className="text-gray-500 text-sm">
                        {item.date}
                      </p>
                    </div>

                    <div className="font-semibold">
                      {item.score}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </main>
  );
}