<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class () extends Migration {
    public function up(): void
    {
        Schema::table('incident_resource', function (Blueprint $table): void {
            $table->string('status', 20)->default('new')->after('resource_id');
        });
    }

    public function down(): void
    {
        Schema::table('incident_resource', function (Blueprint $table): void {
            $table->dropColumn('status');
        });
    }
};
