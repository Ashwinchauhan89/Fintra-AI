const AuthLayout = ({ children }) => {
  return (
    <div className="flex justify-center items-center min-h-screen py-24 px-4 bg-black relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-gsap-green/10 rounded-full blur-[130px] pointer-events-none" />
      <div className="absolute inset-0 dot-grid opacity-30 pointer-events-none" />
      <div className="relative z-10 w-full max-w-md flex justify-center">
        {children}
      </div>
    </div>
  );
};

export default AuthLayout;

